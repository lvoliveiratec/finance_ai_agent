import os
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from google.api_core import exceptions as google_exceptions
from google.cloud import bigquery


PROJECT_ID = os.getenv("BQ_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "hml-data-clean"))
DATASET = os.getenv("BQ_DATASET", "poc_financeiro")
LOCATION = os.getenv("BQ_LOCATION", "US")
MAX_BYTES_BILLED = int(os.getenv("MAX_BYTES_BILLED", str(100 * 1024 * 1024)))

BLOCKED_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "MERGE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "EXPORT",
    "CALL",
    "GRANT",
    "REVOKE",
]


def _load_allowed_tables() -> set[str]:
    catalog_path = Path(__file__).parent / "finance_catalog.yaml"
    with catalog_path.open("r", encoding="utf-8") as file:
        catalog = yaml.safe_load(file)

    allowed = set()
    for view_config in catalog["views_permitidas"].values():
        table = view_config["tabela"]
        table = table.replace("hml-data-clean", PROJECT_ID)
        allowed.add(table)
    return allowed


ALLOWED_TABLES = _load_allowed_tables()


def _normalize_sql(sql: str) -> str:
    return " ".join(sql.strip().split())


def _extract_table_refs(sql: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", sql))


def _json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _validate_sql(sql: str) -> tuple[bool, str]:
    normalized = _normalize_sql(sql)
    upper_sql = normalized.upper()

    if not upper_sql.startswith("SELECT") and not upper_sql.startswith("WITH"):
        return False, "Apenas consultas SELECT ou WITH sao permitidas."

    for keyword in BLOCKED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            return False, f"Comando bloqueado encontrado: {keyword}."

    table_refs = _extract_table_refs(sql)
    if not table_refs:
        return False, "A query precisa referenciar as views permitidas usando crase."

    not_allowed = table_refs - ALLOWED_TABLES
    if not_allowed:
        return False, f"Referencia a tabela/view nao permitida: {sorted(not_allowed)}."

    # BigQuery nao faz coercao automatica entre DATE e STRING. Este caso
    # apareceu quando o agente gerou filtros como mes = '2026-05-01'.
    if re.search(r"\bmes\s*=\s*'\d{4}-\d{2}-\d{2}'", normalized, flags=re.IGNORECASE):
        return False, "Campos DATE devem ser comparados com DATE 'YYYY-MM-DD', nao com string."

    return True, "SQL validado com sucesso."


def consultar_bigquery(sql: str) -> dict:
    """
    Executa uma consulta financeira segura no BigQuery.

    Use esta ferramenta somente para perguntas sobre dados financeiros.
    A consulta deve usar apenas SELECT ou WITH e somente as views permitidas
    no catalogo financeiro.

    Args:
        sql: Query SQL em BigQuery Standard SQL.

    Returns:
        Resultado da consulta com linhas, total de linhas e bytes estimados.
    """
    is_valid, message = _validate_sql(sql)
    if not is_valid:
        return {"status": "erro", "mensagem": message}

    client = bigquery.Client(project=PROJECT_ID, location=LOCATION)

    dry_job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    try:
        dry_job = client.query(sql, job_config=dry_job_config, location=LOCATION)
    except google_exceptions.BadRequest as error:
        return {
            "status": "erro",
            "mensagem": "A SQL gerada nao e valida no BigQuery.",
            "detalhe": str(error),
            "sql_rejeitado": sql,
            "orientacao": "Corrija a SQL e tente novamente. Para campos DATE, use DATE 'YYYY-MM-DD'.",
        }
    except google_exceptions.GoogleAPIError as error:
        return {
            "status": "erro",
            "mensagem": "Erro ao validar a consulta no BigQuery.",
            "detalhe": str(error),
            "sql_rejeitado": sql,
        }

    if dry_job.total_bytes_processed and dry_job.total_bytes_processed > MAX_BYTES_BILLED:
        return {
            "status": "erro",
            "mensagem": "Consulta bloqueada por exceder o limite de bytes processados.",
            "bytes_estimados": dry_job.total_bytes_processed,
            "limite_bytes": MAX_BYTES_BILLED,
        }

    job_config = bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED)
    try:
        query_job = client.query(sql, job_config=job_config, location=LOCATION)
        rows = query_job.result(max_results=50)
    except google_exceptions.BadRequest as error:
        return {
            "status": "erro",
            "mensagem": "A consulta foi rejeitada pelo BigQuery.",
            "detalhe": str(error),
            "sql_rejeitado": sql,
            "orientacao": "Revise filtros de data, nomes de campos, agregacoes e tipos usados na query.",
        }
    except google_exceptions.GoogleAPIError as error:
        return {
            "status": "erro",
            "mensagem": "Erro ao executar a consulta no BigQuery.",
            "detalhe": str(error),
            "sql_rejeitado": sql,
        }

    resultado = [
        {key: _json_safe(value) for key, value in row.items()}
        for row in rows
    ]

    return {
        "status": "sucesso",
        "bytes_estimados": dry_job.total_bytes_processed,
        "total_linhas_retornadas": len(resultado),
        "linhas": resultado,
        "sql_executado": sql,
    }
