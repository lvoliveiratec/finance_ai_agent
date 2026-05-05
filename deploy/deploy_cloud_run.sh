#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-hml-data-clean}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-finance-ai-chat-adapter}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-}"
CHARTS_BUCKET="${CHARTS_BUCKET:-}"
CHARTS_PREFIX="${CHARTS_PREFIX:-finance-ai-poc/charts}"
CHARTS_PUBLIC_BASE_URL="${CHARTS_PUBLIC_BASE_URL:-}"

gcloud config set project "${PROJECT_ID}"

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  chat.googleapis.com \
  --project "${PROJECT_ID}"

DEPLOY_ARGS=(
  "${SERVICE_NAME}"
  --source . \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},BQ_PROJECT_ID=${PROJECT_ID},BQ_DATASET=poc_financeiro,BQ_LOCATION=US,MAX_BYTES_BILLED=104857600,CHARTS_BUCKET=${CHARTS_BUCKET},CHARTS_PREFIX=${CHARTS_PREFIX},CHARTS_PUBLIC_BASE_URL=${CHARTS_PUBLIC_BASE_URL}"
)

if [[ -n "${SERVICE_ACCOUNT}" ]]; then
  DEPLOY_ARGS+=(--service-account "${SERVICE_ACCOUNT}")
fi

gcloud run deploy "${DEPLOY_ARGS[@]}"
