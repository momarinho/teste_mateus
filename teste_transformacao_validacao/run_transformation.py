import os
import re
import zipfile

import pandas as pd

# --- Caminhos dos Arquivos ---
# Saída do Teste 1
CONSOLIDATED_CSV_PATH = os.path.join("data", "processed", "consolidado_despesas.csv")
# Saída da Etapa 2.1
VALIDATED_CSV_PATH = os.path.join(
    "teste_transformacao_validacao", "2.1_dados_validados.csv"
)
# Arquivo de dados cadastrais a ser baixado
OPERADORAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
OPERADORAS_LOCAL_PATH = os.path.join(
    "teste_transformacao_validacao", "operadoras_ativas.csv"
)
# Saída da Etapa 2.2
ENRICHED_CSV_PATH = os.path.join(
    "teste_transformacao_validacao", "2.2_dados_enriquecidos.csv"
)
# Saída da Etapa 2.3
AGGREGATED_CSV_PATH = os.path.join(
    "teste_transformacao_validacao", "despesas_agregadas.csv"
)
AGGREGATED_ZIP_NAME = os.getenv("TESTE_ZIP_NAME", "Teste_Mateus.zip")
AGGREGATED_ZIP_PATH = os.path.join("teste_transformacao_validacao", AGGREGATED_ZIP_NAME)


def validar_cnpj(cnpj: str) -> bool:
    """Valida um CNPJ com base no formato e nos dígitos verificadores."""
    cnpj = "".join(re.findall(r"\d", str(cnpj)))
    if len(cnpj) != 14:
        return False
    if len(set(cnpj)) == 1:
        return False

    # Validação do primeiro dígito verificador
    soma = sum(int(cnpj[i]) * (5 - i if i < 4 else 13 - i) for i in range(12))
    dv1 = 0 if (soma % 11) < 2 else 11 - (soma % 11)
    if dv1 != int(cnpj[12]):
        return False

    # Validação do segundo dígito verificador
    soma = sum(int(cnpj[i]) * (6 - i if i < 5 else 14 - i) for i in range(13))
    dv2 = 0 if (soma % 11) < 2 else 11 - (soma % 11)
    if dv2 != int(cnpj[13]):
        return False

    return True


def run_validation():
    """Executa a etapa de validação dos dados do arquivo consolidado."""
    print("--- Iniciando Etapa 2.1: Validação de Dados ---")
    if not os.path.exists(CONSOLIDATED_CSV_PATH):
        print(f"Erro: Arquivo consolidado não encontrado em '{CONSOLIDATED_CSV_PATH}'.")
        print("Por favor, execute os scripts do Teste 1 primeiro.")
        return None

    df = pd.read_csv(CONSOLIDATED_CSV_PATH, dtype={"CNPJ": str, "RazaoSocial": str})
    print(f"{len(df)} linhas carregadas para validação.")

    validation_issues = [[] for _ in range(len(df))]
    is_cnpj_valid = df["CNPJ"].apply(validar_cnpj)
    for i, is_valid in enumerate(is_cnpj_valid):
        if not is_valid:
            validation_issues[i].append("cnpj_invalido")

    df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")
    for i, value in enumerate(df["ValorDespesas"]):
        if pd.isna(value) or value <= 0:
            validation_issues[i].append("valor_nao_positivo")

    for i, razao in enumerate(df["RazaoSocial"]):
        if pd.isna(razao) or str(razao).strip() == "":
            validation_issues[i].append("razao_social_vazia")

    df["problemas_validacao"] = [
        ",".join(issues) if issues else "" for issues in validation_issues
    ]

    cols = [
        "CNPJ",
        "RazaoSocial",
        "Trimestre",
        "Ano",
        "ValorDespesas",
        "problemas_validacao",
    ]
    df = df[cols]

    df.to_csv(VALIDATED_CSV_PATH, index=False, sep=";", decimal=",")
    print(f"Arquivo com dados validados salvo em: '{VALIDATED_CSV_PATH}'")

    issues_series = (
        pd.Series(df.loc[:, "problemas_validacao"]).fillna("").astype("string")
    )
    total_issues = issues_series.str.get_dummies(sep=",").sum()
    print("\nResumo dos problemas de validação encontrados:")
    print(total_issues)
    print("--- Etapa 2.1 Concluída ---\n")
    return df


def run_enrichment(df_validated):
    """Executa a etapa de enriquecimento de dados."""
    print("--- Iniciando Etapa 2.2: Enriquecimento de Dados ---")
    if df_validated is None:
        print("Etapa de enriquecimento pulada pois não há dados da etapa anterior.")
        return None

    try:
        print(f"Baixando dados cadastrais de '{OPERADORAS_URL}'...")
        df_operadoras = pd.read_csv(
            OPERADORAS_URL, sep=";", encoding="latin1", dtype={"CNPJ": str}
        )
        df_operadoras.to_csv(OPERADORAS_LOCAL_PATH, index=False, sep=";")
        print(f"Dados cadastrais salvos em '{OPERADORAS_LOCAL_PATH}'")
    except Exception as e:
        print(f"Erro ao baixar ou processar o arquivo de operadoras: {e}")
        return None

    df_operadoras.drop_duplicates(subset="CNPJ", keep="last", inplace=True)

    cols_to_join = ["CNPJ", "REGISTRO_OPERADORA", "Modalidade", "UF"]
    df_operadoras_subset: pd.DataFrame = df_operadoras.loc[:, cols_to_join]
    df_operadoras_join = df_operadoras_subset.rename(
        columns={"REGISTRO_OPERADORA": "RegistroANS"}
    )

    df_to_join = df_validated[df_validated["problemas_validacao"] == ""].copy()
    print(f"Número de linhas com CNPJ válido para enriquecimento: {len(df_to_join)}")

    df_enriched = pd.merge(df_validated, df_operadoras_join, on="CNPJ", how="left")

    df_enriched.to_csv(ENRICHED_CSV_PATH, index=False, sep=";", decimal=",")
    print(f"Arquivo com dados enriquecidos salvo em: '{ENRICHED_CSV_PATH}'")

    matched_rows = df_enriched["RegistroANS"].notna().sum()
    print("\nAnálise Crítica do Join:")
    print(
        f" - {matched_rows} de {len(df_enriched)} linhas foram enriquecidas com sucesso."
    )
    print(
        f" - {len(df_enriched) - matched_rows} linhas não encontraram correspondência de CNPJ no cadastro."
    )

    print("--- Etapa 2.2 Concluída ---\n")
    return df_enriched


def run_aggregation(df_enriched):
    """Executa a etapa de agregacao dos dados."""
    print("--- Iniciando Etapa 2.3: Agregacao de Dados ---")
    if df_enriched is None:
        print("Etapa de agregacao pulada pois nao ha dados da etapa anterior.")
        return None

    df_valid = df_enriched[df_enriched["problemas_validacao"] == ""].copy()
    if df_valid.empty:
        print("Nenhuma linha valida para agregacao.")
        df_agg = pd.DataFrame(
            columns=pd.Index(
                [
                    "RazaoSocial",
                    "UF",
                    "total_despesas",
                    "media_despesas_trimestre",
                    "desvio_padrao_despesas",
                ]
            )
        )
        df_agg.to_csv(AGGREGATED_CSV_PATH, index=False, sep=";", decimal=",")
        print(f"Arquivo com despesas agregadas salvo em: '{AGGREGATED_CSV_PATH}'")
        os.makedirs(os.path.dirname(AGGREGATED_ZIP_PATH), exist_ok=True)
        with zipfile.ZipFile(
            AGGREGATED_ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            zf.write(AGGREGATED_CSV_PATH, arcname=os.path.basename(AGGREGATED_CSV_PATH))
        print(f"Arquivo compactado salvo em: '{AGGREGATED_ZIP_PATH}'")
        print("--- Etapa 2.3 Concluida ---\n")
        return df_agg

    df_valid["ValorDespesas"] = pd.to_numeric(
        df_valid["ValorDespesas"], errors="coerce"
    )
    df_valid["Ano"] = pd.to_numeric(df_valid["Ano"], errors="coerce")
    df_valid["Trimestre"] = pd.to_numeric(df_valid["Trimestre"], errors="coerce")

    quarterly_base = df_valid.dropna(subset=["Ano", "Trimestre"])
    quarterly_totals = (
        quarterly_base.groupby(
            ["RazaoSocial", "UF", "Ano", "Trimestre"], dropna=False, as_index=False
        )["ValorDespesas"]
        .sum()
        .rename(columns={"ValorDespesas": "total_trimestre"})
    )

    totals = (
        df_valid.groupby(["RazaoSocial", "UF"], dropna=False, as_index=False)[
            "ValorDespesas"
        ]
        .sum()
        .rename(columns={"ValorDespesas": "total_despesas"})
    )

    stats = quarterly_totals.groupby(
        ["RazaoSocial", "UF"], dropna=False, as_index=False
    )["total_trimestre"].agg(
        media_despesas_trimestre="mean",
        desvio_padrao_despesas="std",
    )

    df_agg = totals.merge(stats, on=["RazaoSocial", "UF"], how="left")
    df_agg = df_agg.sort_values("total_despesas", ascending=False)

    df_agg.to_csv(AGGREGATED_CSV_PATH, index=False, sep=";", decimal=",")
    print(f"Arquivo com despesas agregadas salvo em: '{AGGREGATED_CSV_PATH}'")
    os.makedirs(os.path.dirname(AGGREGATED_ZIP_PATH), exist_ok=True)
    with zipfile.ZipFile(
        AGGREGATED_ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        zf.write(AGGREGATED_CSV_PATH, arcname=os.path.basename(AGGREGATED_CSV_PATH))
    print(f"Arquivo compactado salvo em: '{AGGREGATED_ZIP_PATH}'")

    print("--- Etapa 2.3 Concluida ---\n")
    return df_agg


def main():
    print("--- Iniciando Teste 2: Transformação e Validação de Dados ---\n")

    # Etapa 2.1: Validação
    df_validated = run_validation()

    # Etapa 2.2: Enriquecimento
    df_enriched = run_enrichment(df_validated)

    # Etapa 2.3: Agregação
    run_aggregation(df_enriched)

    print("\n--- Teste 2 concluído ---")


if __name__ == "__main__":
    main()
