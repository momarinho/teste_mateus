import os
import re

import numpy as np
import pandas as pd

# Caminho para o arquivo CSV consolidado do Teste 1
CONSOLIDATED_CSV_PATH = os.path.join("data", "processed", "consolidado_despesas.csv")

# Caminho para o arquivo de saída após a validação
VALIDATED_CSV_PATH = os.path.join(
    "teste_transformacao_validacao", "2.1_dados_validados.csv"
)


def validar_cnpj(cnpj: str) -> bool:
    """Valida um CNPJ com base no formato e nos dígitos verificadores."""
    # Remove caracteres não numéricos
    cnpj = "".join(re.findall(r"\d", str(cnpj)))

    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False

    # Elimina CNPJs com todos os dígitos iguais
    if len(set(cnpj)) == 1:
        return False

    # Validação do primeiro dígito verificador
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj[i]) * peso
        peso -= 1
        if peso < 2:
            peso = 9
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    if dv1 != int(cnpj[12]):
        return False

    # Validação do segundo dígito verificador
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj[i]) * peso
        peso -= 1
        if peso < 2:
            peso = 9
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    if dv2 != int(cnpj[13]):
        return False

    return True


def run_validation():
    """
    Executa a etapa de validação dos dados do arquivo consolidado.
    """
    print(f"Carregando dados de '{CONSOLIDATED_CSV_PATH}'...")
    if not os.path.exists(CONSOLIDATED_CSV_PATH):
        print(f"Erro: Arquivo consolidado não encontrado em '{CONSOLIDATED_CSV_PATH}'.")
        print("Por favor, execute os scripts do Teste 1 primeiro.")
        return

    df = pd.read_csv(CONSOLIDATED_CSV_PATH, dtype={"CNPJ": str})
    print(f"{len(df)} linhas carregadas.")

    print("Iniciando validação de dados...")

    # Lista para armazenar os problemas de cada linha
    validation_issues = [[] for _ in range(len(df))]

    # 1. Validação de CNPJ
    # A função `validar_cnpj` será aplicada a cada CNPJ
    is_cnpj_valid = df["CNPJ"].apply(validar_cnpj)
    for i, is_valid in enumerate(is_cnpj_valid):
        if not is_valid:
            validation_issues[i].append("cnpj_invalido")

    # 2. Validação de Valores Numéricos Positivos
    # Converte 'ValorDespesas' para numérico, tratando erros
    df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")
    for i, value in enumerate(df["ValorDespesas"]):
        if pd.isna(value) or value <= 0:
            validation_issues[i].append("valor_nao_positivo")

    # 3. Validação de Razão Social não vazia
    for i, razao in enumerate(df["RazaoSocial"]):
        if pd.isna(razao) or str(razao).strip() == "":
            validation_issues[i].append("razao_social_vazia")

    # Adiciona a coluna com os problemas de validação
    df["problemas_validacao"] = [
        ",".join(issues) if issues else "" for issues in validation_issues
    ]

    # Reorganiza as colunas para melhor visualização
    cols = [
        "CNPJ",
        "RazaoSocial",
        "Trimestre",
        "Ano",
        "ValorDespesas",
        "problemas_validacao",
    ]
    df = df[cols]

    print("Validação concluída.")

    # Salva o arquivo validado
    df.to_csv(VALIDATED_CSV_PATH, index=False, sep=";", decimal=",")
    print(f"Arquivo com dados validados salvo em: '{VALIDATED_CSV_PATH}'")

    # Exibe um resumo dos problemas encontrados
    total_issues = df["problemas_validacao"].str.get_dummies(sep=",").sum()
    print("\nResumo dos problemas de validação encontrados:")
    print(total_issues)


def main():
    print("--- Iniciando Teste 2: Transformação e Validação de Dados ---")

    # Etapa 2.1: Validação
    run_validation()

    # Próximas etapas (2.2 e 2.3) serão adicionadas aqui.

    print("\n--- Teste 2 concluído ---")


if __name__ == "__main__":
    main()
