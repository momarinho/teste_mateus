import argparse
import csv
import json
import os
import re
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

try:
    import openpyxl  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    openpyxl = None


DEFAULT_INPUT_DIR = os.path.join("data", "demonstracoes_contabeis")
DEFAULT_EXTRACT_DIR = os.path.join("data", "extracted")
DEFAULT_OUTPUT_DIR = os.path.join("data", "processed")

SUPPORTED_EXTENSIONS = {".csv", ".txt", ".xlsx", ".xls"}


def list_zip_files(input_dir: str, manifest_path: Optional[str]) -> List[str]:
    if manifest_path and os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        files = []
        for entry in payload.get("entries", []):
            url = entry.get("url", "")
            local_path = entry.get("local_path")
            if url.lower().endswith(".zip") and local_path:
                files.append(local_path)
        return files

    zip_files = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if name.lower().endswith(".zip"):
                zip_files.append(os.path.join(root, name))
    return zip_files


def extract_zip(zip_path: str, extract_dir: str, overwrite: bool) -> str:
    base_name = os.path.splitext(os.path.basename(zip_path))[0]
    target_dir = os.path.join(extract_dir, base_name)
    if os.path.exists(target_dir) and not overwrite:
        return target_dir
    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)
    return target_dir


def iter_data_files(extract_dirs: Iterable[str]) -> Iterable[str]:
    for extract_dir in extract_dirs:
        for root, _, files in os.walk(extract_dir):
            for name in files:
                ext = os.path.splitext(name)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    yield os.path.join(root, name)


def normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_column_name(name: str) -> str:
    name = normalize_text(name)
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


def detect_delimiter(sample_line: str) -> str:
    candidates = [";", ",", "\t", "|"]
    counts = {c: sample_line.count(c) for c in candidates}
    return max(counts, key=lambda c: counts[c])


def open_text_file(path: str):
    try:
        return open(path, "r", encoding="utf-8-sig", errors="replace", newline="")
    except Exception:
        return open(path, "r", encoding="latin-1", errors="replace", newline="")


def guess_columns(columns: List[str]) -> Dict[str, Optional[str]]:
    normalized = {col: normalize_column_name(col) for col in columns}

    def pick_column(choices: List[Tuple[Tuple[str, ...], int]]) -> Optional[str]:
        best_col = None
        best_score = 0
        for col, norm in normalized.items():
            score = 0
            for keywords, weight in choices:
                if any(keyword in norm for keyword in keywords):
                    score = max(score, weight)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

    return {
        "cnpj": pick_column([(("cnpj",), 3)]),
        "reg_ans": pick_column(
            [
                (("regans", "registroans", "registro", "ans"), 2),
                (("reg",), 1),
            ]
        ),
        "razao_social": pick_column(
            [
                (("razaosocial",), 3),
                (("razao", "nomerazao"), 2),
                (("operadora", "nome"), 1),
            ]
        ),
        "descricao": pick_column(
            [
                (("descricao", "desc"), 3),
                (("nomeconta",), 2),
                (("conta", "item"), 1),
            ]
        ),
        "valor": pick_column(
            [
                (("saldofinal", "valorfinal"), 3),
                (("saldo",), 2),
                (("valor", "vlr", "valores"), 1),
            ]
        ),
        "competencia": pick_column(
            [
                (("compet", "periodo", "referencia"), 3),
                (("data", "dt"), 2),
            ]
        ),
    }


def is_despesa_evento(value: str) -> bool:
    text = normalize_text(value)
    if "despesa" not in text:
        return False
    return "evento" in text or "sinistro" in text


def parse_number(value: str) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("R$", "").replace(" ", "")
    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", "")

    try:
        value_num = float(text)
    except ValueError:
        return None
    return -value_num if negative else value_num


def extract_year_quarter(value: str) -> Tuple[Optional[int], Optional[int]]:
    text = normalize_text(str(value))
    match = re.search(r"(20\d{2})[-/\.]?(0[1-9]|1[0-2])", text)
    if not match:
        match = re.search(r"(20\d{2})", text)
        if not match:
            return None, None
        return int(match.group(1)), None
    year = int(match.group(1))
    month = int(match.group(2))
    quarter = (month - 1) // 3 + 1
    return year, quarter


def build_output_writer(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_file = open(output_path, "w", encoding="utf-8", newline="")
    writer = csv.writer(output_file)
    writer.writerow(
        [
            "cnpj",
            "reg_ans",
            "razao_social",
            "valor_despesas",
            "descricao",
            "competencia_raw",
            "ano",
            "trimestre",
            "source_file",
        ]
    )
    return output_file, writer


def normalize_row(
    row: Dict[str, str],
    mapping: Dict[str, Optional[str]],
    source_file: str,
) -> Optional[List[str]]:
    descricao_col = mapping.get("descricao")
    if descricao_col and row.get(descricao_col) is not None:
        if not is_despesa_evento(str(row.get(descricao_col))):
            return None
    else:
        if not any(is_despesa_evento(str(value)) for value in row.values()):
            return None

    def get_value(key: Optional[str]) -> str:
        if not key:
            return ""
        return row.get(key, "")

    cnpj_value = get_value(mapping.get("cnpj"))
    cnpj_digits = re.sub(r"\D", "", str(cnpj_value)) if cnpj_value else ""

    reg_ans_value = get_value(mapping.get("reg_ans"))

    razao_value = get_value(mapping.get("razao_social"))
    valor_value = get_value(mapping.get("valor"))
    competencia_value = get_value(mapping.get("competencia"))

    valor_num = parse_number(valor_value)
    ano, trimestre = extract_year_quarter(competencia_value)

    return [
        cnpj_digits,
        str(reg_ans_value).strip(),
        str(razao_value).strip(),
        "" if valor_num is None else f"{valor_num:.2f}",
        str(get_value(descricao_col)).strip(),
        str(competencia_value).strip(),
        "" if ano is None else str(ano),
        "" if trimestre is None else str(trimestre),
        source_file,
    ]


def process_csv_file(
    path: str, output_path: str, manifest_entry: Dict[str, Any]
) -> int:
    with open_text_file(path) as f:
        first_line = f.readline()
        if not first_line:
            return 0
        delimiter = detect_delimiter(first_line)
        f.seek(0)
        reader = csv.reader(f, delimiter=delimiter)
        try:
            header = next(reader)
        except StopIteration:
            return 0
        mapping = guess_columns(header)
        manifest_entry["columns"] = mapping
        output_file, writer = build_output_writer(output_path)
        rows_written = 0
        try:
            for row in reader:
                row_dict = {
                    col: (row[idx] if idx < len(row) else "")
                    for idx, col in enumerate(header)
                }
                normalized = normalize_row(row_dict, mapping, os.path.basename(path))
                if normalized is None:
                    continue
                writer.writerow(normalized)
                rows_written += 1
        finally:
            output_file.close()
        return rows_written


def process_xlsx_file(
    path: str, output_path: str, manifest_entry: Dict[str, Any]
) -> int:
    if openpyxl is None:
        raise RuntimeError(
            "openpyxl nao esta instalado. Instale com: pip install openpyxl"
        )
    openpyxl_mod = cast(Any, openpyxl)
    workbook = openpyxl_mod.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)
    try:
        header = next(rows)
    except StopIteration:
        return 0
    columns = [str(col) if col is not None else "" for col in header]
    mapping = guess_columns(columns)
    manifest_entry["columns"] = mapping
    output_file, writer = build_output_writer(output_path)
    rows_written = 0
    try:
        for row in rows:
            row_values = ["" if value is None else str(value) for value in row]
            row_dict = {
                col: (row_values[idx] if idx < len(row_values) else "")
                for idx, col in enumerate(columns)
            }
            normalized = normalize_row(row_dict, mapping, os.path.basename(path))
            if normalized is None:
                continue
            writer.writerow(normalized)
            rows_written += 1
    finally:
        output_file.close()
        workbook.close()
    return rows_written


def process_file(path: str, output_dir: str) -> Dict[str, Any]:
    ext = os.path.splitext(path)[1].lower()
    output_path = os.path.join(output_dir, "normalized", f"{Path(path).stem}.csv")
    manifest_entry: Dict[str, Any] = {
        "source_file": path,
        "output_file": output_path,
        "rows_written": "0",
        "status": "skipped",
    }
    try:
        if ext in {".csv", ".txt"}:
            count = process_csv_file(path, output_path, manifest_entry)
        elif ext in {".xlsx", ".xls"}:
            count = process_xlsx_file(path, output_path, manifest_entry)
        else:
            return manifest_entry
        manifest_entry["rows_written"] = str(count)
        manifest_entry["status"] = "processed"
    except Exception as exc:
        manifest_entry["status"] = "error"
        manifest_entry["error"] = str(exc)
    return manifest_entry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Processa os arquivos da ANS e extrai despesas com eventos/sinistros."
    )
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR)
    parser.add_argument("--extract-dir", default=DEFAULT_EXTRACT_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--manifest", default=os.path.join(DEFAULT_INPUT_DIR, "manifest.json")
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    zip_files = list_zip_files(args.input_dir, args.manifest)
    if not zip_files:
        print("Nenhum ZIP encontrado. Rode o download (1.1) antes.")
        return 1

    extract_dirs = []
    error_entries = []
    for zip_path in zip_files:
        if not os.path.exists(zip_path):
            error_entries.append(
                {
                    "stage": "extract",
                    "file": zip_path,
                    "error": "arquivo_nao_encontrado",
                }
            )
            continue
        try:
            extract_dirs.append(extract_zip(zip_path, args.extract_dir, args.overwrite))
        except Exception as exc:
            error_entries.append(
                {"stage": "extract", "file": zip_path, "error": str(exc)}
            )

    if not extract_dirs:
        print("Nenhum ZIP valido para extrair.")
        return 1

    manifest_entries = []
    for file_path in iter_data_files(extract_dirs):
        entry = process_file(file_path, args.output_dir)
        manifest_entries.append(entry)
        status = entry.get("status")
        if status == "error":
            error_entries.append(
                {
                    "stage": "process",
                    "file": file_path,
                    "error": entry.get("error", "erro_desconhecido"),
                }
            )
        print(f"{status}: {file_path}")

    os.makedirs(args.output_dir, exist_ok=True)
    manifest_path = os.path.join(args.output_dir, "process_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "input_dir": args.input_dir,
                "extract_dir": args.extract_dir,
                "output_dir": args.output_dir,
                "summary": {
                    "processed": sum(
                        1 for e in manifest_entries if e.get("status") == "processed"
                    ),
                    "skipped": sum(
                        1 for e in manifest_entries if e.get("status") == "skipped"
                    ),
                    "error": sum(
                        1 for e in manifest_entries if e.get("status") == "error"
                    ),
                },
                "errors": error_entries,
                "entries": manifest_entries,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print("Manifest salvo em:", manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
