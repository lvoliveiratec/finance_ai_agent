"""
Template para deploy futuro no Vertex AI Agent Engine.

A POC atual roda o agente localmente ou dentro do Cloud Run Chat Adapter.
Quando a decisao for usar Agent Engine como runtime gerenciado, este arquivo
deve ser ajustado conforme a versao do SDK instalada no ambiente de deploy.
"""

import os

import vertexai
from vertexai import agent_engines

from finance_ai_agent.agent import root_agent


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "hml-data-clean")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def main() -> None:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    remote_agent = agent_engines.create(
        root_agent,
        requirements=[
            "google-adk",
            "google-cloud-bigquery",
            "PyYAML",
        ],
        display_name="finance-ai-agent-poc",
        description="Agente financeiro da POC para consultar BigQuery.",
    )

    print(remote_agent.resource_name)


if __name__ == "__main__":
    main()
