#!/bin/bash
set -euxo pipefail
export AWS_DEFAULT_REGION=us-east-1

# Retrieve secrets
DB_SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:523180269986:secret:DbCredentials798065DE-3hWEhASODaiu-g1KKcJ --query SecretString --output text)
DB_USER=$(echo "$DB_SECRET_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["username"])')
DB_PASSWORD=$(echo "$DB_SECRET_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["password"])')
FLASK_SECRET=$(aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:523180269986:secret:FlaskSecretDB73E49F-BolLAxSBwenS-nu5YVv --query SecretString --output text)
GOOGLE_CLIENT_ID=$(aws ssm get-parameter --name /northflow/prod/google-client-id --query Parameter.Value --output text)
GOOGLE_SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:523180269986:secret:GoogleClientSecret-xgQfKr --query SecretString --output text)
GOOGLE_CLIENT_SECRET=$(echo "$GOOGLE_SECRET_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["GOOGLE_CLIENT_SECRET"])')

# Stop and remove existing container
docker stop northflow || true
docker rm northflow || true

# Start new container with OAuth credentials
docker run -d --restart unless-stopped --name northflow -p 80:8000 \
  --env FLASK_ENV=production \
  --env DB_HOST=northflow-prod-database-mysqlinstance2cfb48f1-gtf9zfuoqq6l.co98ucik0bye.us-east-1.rds.amazonaws.com \
  --env DB_PORT=3306 \
  --env DB_NAME=northflow \
  --env DB_USER="$DB_USER" \
  --env DB_PASSWORD="$DB_PASSWORD" \
  --env SECRET_KEY="$FLASK_SECRET" \
  --env GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
  --env GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
  northflow:latest

# Wait and verify
sleep 5
docker ps | grep northflow
curl -f http://localhost/health || echo 'Health check failed'
