import os
import re
from datetime import datetime, timezone
from io import BytesIO
from typing import Any
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from google.api_core import exceptions as google_exceptions
from google.cloud import storage

from .bigquery_tool import consultar_bigquery


CHARTS_BUCKET = os.getenv("CHARTS_BUCKET", "")
CHARTS_PREFIX = os.getenv("CHARTS_PREFIX", "finance-ai-poc/charts")
CHARTS_PUBLIC_BASE_URL = os.getenv("CHARTS_PUBLIC_BASE_URL", "")
MAKE_CHARTS_PUBLIC = os.getenv("MAKE_CHARTS_PUBLIC", "false").lower() == "true"

FIELD_LABELS = {
    "mes": "Mês",
    "centro_custo": "Centro de custo",
    "fornecedor": "Fornecedor",
    "categoria": "Categoria",
    "unidade": "Unidade",
    "area": "Área",
    "valor": "Valor",
    "valor_realizado": "Realizado",
    "valor_orcado": "Orçado",
    "variacao_valor": "Variação",
    "receita_realizada": "Receita",
    "despesa_realizada": "Despesa",
    "valor_despesa": "Despesa",
    "total_gasto": "Gasto",
    "total_despesa": "Despesa",
    "despesa_total": "Despesa",
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:60] or "grafico"


def _as_number(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace("R$", "").replace(".", "").replace(",", ".").strip())


def _format_label(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        year, month, _ = text.split("-")
        return f"{month}/{year}"
    return text


def _format_currency(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def _field_label(field_name: str) -> str:
    return FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())


def _build_chart(rows: list[dict[str, Any]], titulo: str, eixo_x: str, eixos_y: list[str], tipo: str) -> BytesIO:
    labels = [_format_label(row.get(eixo_x)) for row in rows]
    series_values = {
        eixo_y: [_as_number(row.get(eixo_y)) for row in rows]
        for eixo_y in eixos_y
    }

    fig_width = max(8, min(14, len(labels) * 1.2))
    fig, ax = plt.subplots(figsize=(fig_width, 5.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    chart_type = tipo.lower().strip()
    colors = ["#006CFF", "#19A974", "#FFB000", "#D64550", "#7B61FF"]

    if chart_type in {"linha", "line"}:
        for index, eixo_y in enumerate(eixos_y):
            values = series_values[eixo_y]
            ax.plot(
                labels,
                values,
                marker="o",
                linewidth=2.5,
                color=colors[index % len(colors)],
                label=_field_label(eixo_y),
            )

            if len(eixos_y) <= 2 and len(labels) <= 8:
                for point_index, value in enumerate(values):
                    ax.annotate(
                        _format_currency(value),
                        (point_index, value),
                        textcoords="offset points",
                        xytext=(0, 8),
                        ha="center",
                        fontsize=9,
                    )
    else:
        x_positions = list(range(len(labels)))
        bar_width = min(0.8 / max(len(eixos_y), 1), 0.35)
        offset_start = -((len(eixos_y) - 1) * bar_width) / 2

        for index, eixo_y in enumerate(eixos_y):
            values = series_values[eixo_y]
            positions = [position + offset_start + (index * bar_width) for position in x_positions]
            bars = ax.bar(
                positions,
                values,
                width=bar_width,
                color=colors[index % len(colors)],
                label=_field_label(eixo_y),
            )

            if len(labels) <= 8 and len(eixos_y) <= 2:
                for bar, value in zip(bars, values):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        _format_currency(value),
                        ha="center",
                        va="bottom",
                        fontsize=9,
                    )

        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels)

    ax.set_title(titulo, fontsize=16, fontweight="bold", pad=18)
    ax.set_xlabel(_field_label(eixo_x), fontsize=11)
    ax.set_ylabel(_field_label(eixos_y[0]) if len(eixos_y) == 1 else "Valor", fontsize=11)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: _format_currency(value)))
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=25)

    if len(eixos_y) > 1:
        ax.legend(frameon=False, loc="best")

    fig.tight_layout()
    image = BytesIO()
    fig.savefig(image, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    image.seek(0)
    return image


def _upload_chart(image: BytesIO, titulo: str) -> str:
    if not CHARTS_BUCKET:
        raise ValueError("Variavel de ambiente CHARTS_BUCKET nao configurada.")

    storage_client = storage.Client()
    bucket = storage_client.bucket(CHARTS_BUCKET)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    blob_name = f"{CHARTS_PREFIX.rstrip('/')}/{timestamp}-{_slugify(titulo)}-{uuid4().hex[:8]}.png"
    blob = bucket.blob(blob_name)
    blob.upload_from_file(image, content_type="image/png")

    if MAKE_CHARTS_PUBLIC:
        blob.make_public()

    if CHARTS_PUBLIC_BASE_URL:
        return f"{CHARTS_PUBLIC_BASE_URL.rstrip('/')}/{blob_name}"

    return f"https://storage.googleapis.com/{CHARTS_BUCKET}/{blob_name}"


def criar_grafico_financeiro(
    sql: str,
    titulo: str,
    eixo_x: str,
    eixo_y: str = "",
    tipo: str = "barra",
    eixos_y: list[str] | None = None,
) -> dict:
    """
    Cria um grafico financeiro PNG a partir de uma consulta BigQuery segura.

    Use esta ferramenta quando o usuario pedir grafico, visualizacao, barras,
    linha, evolucao visual ou comparacao visual.

    Args:
        sql: Query SQL em BigQuery Standard SQL usando apenas views permitidas.
        titulo: Titulo do grafico.
        eixo_x: Nome do campo retornado pela SQL para o eixo X.
        eixo_y: Nome do campo numerico retornado pela SQL para o eixo Y. Use para grafico simples.
        tipo: Tipo do grafico: barra ou linha.
        eixos_y: Lista de campos numericos para graficos com multiplas series.

    Returns:
        Status da geracao e URL publica do PNG quando concluido.
    """
    resultado = consultar_bigquery(sql)
    if resultado.get("status") != "sucesso":
        return resultado

    rows = resultado.get("linhas", [])
    if not rows:
        return {"status": "erro", "mensagem": "A consulta nao retornou dados para gerar o grafico."}

    y_fields = eixos_y or ([eixo_y] if eixo_y else [])
    if not y_fields:
        return {
            "status": "erro",
            "mensagem": "Informe eixo_y para grafico simples ou eixos_y para grafico com multiplas series.",
        }

    missing_fields = [field for field in [eixo_x, *y_fields] if field not in rows[0]]
    if missing_fields:
        return {
            "status": "erro",
            "mensagem": f"Campos ausentes no resultado da SQL: {missing_fields}.",
            "campos_disponiveis": sorted(rows[0].keys()),
        }

    try:
        image = _build_chart(rows=rows, titulo=titulo, eixo_x=eixo_x, eixos_y=y_fields, tipo=tipo)
        url = _upload_chart(image=image, titulo=titulo)
    except ValueError as error:
        return {
            "status": "erro",
            "mensagem": str(error),
            "orientacao": "Configure CHARTS_BUCKET no Cloud Run e crie o bucket no Cloud Storage.",
        }
    except google_exceptions.GoogleAPIError as error:
        return {
            "status": "erro",
            "mensagem": "Erro ao salvar o grafico no Cloud Storage.",
            "detalhe": str(error),
        }

    return {
        "status": "sucesso",
        "titulo": titulo,
        "tipo": tipo,
        "series": y_fields,
        "url": url,
        "total_linhas_usadas": len(rows),
        "sql_executado": resultado.get("sql_executado"),
    }
