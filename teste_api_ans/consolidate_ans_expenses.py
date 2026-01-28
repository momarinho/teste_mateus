import argparse
import csv
import json
import os
import re
import zipfile
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

DEFAULT_INPUT_DIR = os.path.join("data", "processed", "normalized")
DEFAULT_OUTPUT_DIR = os.path.join("data", "processed")


def iter_normalized_files(input_dir: str) -> Iterable[str]:
    for root, _, files in os.walk(input_dir):
        for name in files:
            if name.lower().endswith(".csv"):
                yield os.path.join(root, name)


def normalize_cnpj(value: str) -> str:
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


def consolidate(
    input_dir: str,
) -> Tuple[List[List[str]], List[List[str]], Dict[str, int]]:
    rows_out: List[List[str]] = []
    issue_rows: List[List[str]] = []
    issue_counts: Dict[str, int] = defaultdict(int)
    cnpj_razao: Dict[str, set] = defaultdict(set)

    for path in iter_normalized_files(input_dir):
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cnpj = normalize_cnpj(row.get("cnpj", ""))
                razao = normalize_razao_social(row.get("razao_social", ""))
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

                for issue in issues:
                    issue_counts[issue] += 1

                base_row = [
                    cnpj,
                    razao,
                    "" if quarter is None else str(quarter),
                    "" if year is None else str(year),
                    "" if valor is None else f"{valor:.2f}",
                ]
                rows_out.append(base_row)
                if issues:
                    issue_rows.append(
                        base_row
                        + [
                            ",".join(sorted(set(issues))),
                            os.path.basename(path),
                        ]
                    )

    for cnpj, razoes in cnpj_razao.items():
        if len(razoes) > 1:
            issue_counts["cnpj_com_razoes_diferentes"] += 1

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
