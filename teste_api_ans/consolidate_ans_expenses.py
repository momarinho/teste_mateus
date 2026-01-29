import argparse
import csv
import json
import os
import re
import zipfile
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple, TypedDict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class RowEntry(TypedDict):
    cnpj: str
    base_row: List[str]
    issues: List[str]
    source: str


DEFAULT_INPUT_DIR = os.path.join("data", "processed", "normalized")
DEFAULT_OUTPUT_DIR = os.path.join("data", "processed")
OPERADORAS_URL = (
    "https://dadosabertos.ans.gov.br/FTP/PDA/"
    "operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
)
OPERADORAS_LOCAL_PATH = os.path.join("data", "operadoras", "operadoras_ativas.csv")


def iter_normalized_files(input_dir: str) -> Iterable[str]:
    for root, _, files in os.walk(input_dir):
        for name in files:
            if name.lower().endswith(".csv"):
                yield os.path.join(root, name)


def normalize_cnpj(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def normalize_reg_ans(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def parse_number(value: str) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
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
        num = float(text)
    except ValueError:
        return None
    return -num if negative else num


def parse_trimestre_ano(
    row: Dict[str, str],
) -> Tuple[Optional[int], Optional[int], List[str]]:
    issues = []

    ano = row.get("ano", "").strip()
    trimestre = row.get("trimestre", "").strip()
    if ano.isdigit():
        year = int(ano)
    else:
        year = None
        if ano:
            issues.append("ano_invalido")
    if trimestre.isdigit():
        quarter = int(trimestre)
    else:
        quarter = None
        if trimestre:
            issues.append("trimestre_invalido")

    if year is None or quarter is None:
        raw = row.get("competencia_raw", "").strip()
        match = re.search(r"(20\d{2})[-/\.]?(0[1-9]|1[0-2])", raw)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            quarter = (month - 1) // 3 + 1
            issues.append("trimestre_corrigido_competencia")

    return year, quarter, issues


def normalize_razao_social(value: str) -> str:
    return " ".join(value.strip().split()).upper() if value else ""


def normalize_field_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def download_operadoras(url: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = Request(url, headers={"User-Agent": "ans-consolidator/1.0"})
    with urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def load_operadoras_map(path: str, url: str) -> Dict[str, Dict[str, str]]:
    if not os.path.exists(path):
        try:
            download_operadoras(url, path)
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"Aviso: falha ao baixar cadastro de operadoras: {exc}")
            return {}

    try:
        file_obj = open(path, "r", encoding="utf-8-sig", errors="replace", newline="")
    except Exception:
        file_obj = open(path, "r", encoding="latin-1", errors="replace", newline="")

    with file_obj as f:
        reader = csv.DictReader(f, delimiter=";")
        if not reader.fieldnames:
            return {}
        field_map = {normalize_field_name(name): name for name in reader.fieldnames}
        reg_key = (
            field_map.get("registrooperadora")
            or field_map.get("regans")
            or field_map.get("registroans")
        )
        cnpj_key = field_map.get("cnpj")
        razao_key = field_map.get("razaosocial")
        if not reg_key or not cnpj_key or not razao_key:
            return {}

        mapping: Dict[str, Dict[str, str]] = {}
        for row in reader:
            reg_ans = normalize_reg_ans(row.get(reg_key, ""))
            if not reg_ans:
                continue
            mapping[reg_ans] = {
                "cnpj": normalize_cnpj(row.get(cnpj_key, "")),
                "razao": normalize_razao_social(row.get(razao_key, "")),
            }
        return mapping


def consolidate(
    input_dir: str,
) -> Tuple[List[List[str]], List[List[str]], Dict[str, int]]:
    rows_out: List[List[str]] = []
    issue_rows: List[List[str]] = []
    issue_counts: Dict[str, int] = defaultdict(int)
    cnpj_razao: Dict[str, set] = defaultdict(set)
    row_entries: List[RowEntry] = []
    operadoras_map = load_operadoras_map(OPERADORAS_LOCAL_PATH, OPERADORAS_URL)
    if not operadoras_map:
        print(
            "Aviso: cadastro de operadoras indisponivel; "
            "CNPJ/RazaoSocial podem ficar vazios."
        )

    for path in iter_normalized_files(input_dir):
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cnpj = normalize_cnpj(row.get("cnpj", ""))
                razao = normalize_razao_social(row.get("razao_social", ""))
                reg_ans = normalize_reg_ans(row.get("reg_ans", ""))
                if reg_ans and (not cnpj or not razao):
                    mapped = operadoras_map.get(reg_ans)
                    if mapped:
                        if not cnpj:
                            cnpj = mapped.get("cnpj", "")
                        if not razao:
                            razao = mapped.get("razao", "")
                valor = parse_number(row.get("valor_despesas", ""))
                year, quarter, issues = parse_trimestre_ano(row)

                if not cnpj:
                    issues.append("cnpj_ausente")
                if not razao:
                    issues.append("razao_social_ausente")
                if valor is None:
                    issues.append("valor_invalido")
                elif valor <= 0:
                    issues.append("valor_nao_positivo")

                if cnpj and razao:
                    cnpj_razao[cnpj].add(razao)

                base_row = [
                    cnpj,
                    razao,
                    "" if quarter is None else str(quarter),
                    "" if year is None else str(year),
                    "" if valor is None else f"{valor:.2f}",
                ]
                row_entries.append(
                    {
                        "cnpj": cnpj,
                        "base_row": base_row,
                        "issues": issues,
                        "source": os.path.basename(path),
                    }
                )

    duplicated_cnpj = {cnpj for cnpj, razoes in cnpj_razao.items() if len(razoes) > 1}
    for entry in row_entries:
        issues = entry["issues"]
        cnpj = entry["cnpj"]
        if cnpj and cnpj in duplicated_cnpj:
            if "cnpj_com_razoes_diferentes" not in issues:
                issues.append("cnpj_com_razoes_diferentes")
        for issue in issues:
            issue_counts[issue] += 1
        base_row = entry["base_row"]
        rows_out.append(base_row)
        if issues:
            issue_rows.append(
                base_row
                + [
                    ",".join(sorted(set(issues))),
                    entry["source"],
                ]
            )

    return rows_out, issue_rows, dict(issue_counts)


def write_output(rows: List[List[str]], output_csv: str) -> None:
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"])
        writer.writerows(rows)


def write_issues(issue_rows: List[List[str]], output_csv: str) -> None:
    if not issue_rows:
        return
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "CNPJ",
                "RazaoSocial",
                "Trimestre",
                "Ano",
                "ValorDespesas",
                "Issues",
                "SourceFile",
            ]
        )
        writer.writerows(issue_rows)


def zip_output(csv_path: str, zip_path: str) -> None:
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(csv_path, arcname=os.path.basename(csv_path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consolida despesas com eventos/sinistros e analisa inconsistencias."
    )
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-name", default="consolidado_despesas.csv")
    parser.add_argument("--zip-name", default="consolidado_despesas.zip")
    args = parser.parse_args()

    rows, issue_rows, issue_counts = consolidate(args.input_dir)
    if not rows:
        print("Nenhum dado consolidado. Verifique o input_dir.")
        return 1

    output_csv = os.path.join(args.output_dir, args.output_name)
    write_output(rows, output_csv)
    issues_csv = os.path.join(args.output_dir, "consolidado_inconsistencias.csv")
    write_issues(issue_rows, issues_csv)
    zip_output(output_csv, os.path.join(args.output_dir, args.zip_name))
    issues_summary_path = os.path.join(args.output_dir, "inconsistencias_resumo.json")
    with open(issues_summary_path, "w", encoding="utf-8") as f:
        json.dump(issue_counts, f, ensure_ascii=False, indent=2)

    print("CSV consolidado em:", output_csv)
    print("CSV de inconsistencias em:", issues_csv)
    print("ZIP gerado em:", os.path.join(args.output_dir, args.zip_name))
    print("Resumo de inconsistencias em:", issues_summary_path)
    print("Inconsistencias encontradas:")
    for key, value in sorted(issue_counts.items()):
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
