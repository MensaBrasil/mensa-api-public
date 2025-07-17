[![codecov](https://codecov.io/gh/MensaBrasil/mensa-api/graph/badge.svg?token=OQMRVG99CM)](https://codecov.io/gh/MensaBrasil/mensa-api)

Geração das imagens dos Certificados: Credito Marcos Rebello (MB 135)

## Features
- **Authentication and Security**: Utilizes Firebase token verification and secret key validation for secure access.
- **User Management**: Create and manage users in Google Workspace.
- **Member Management**: Manage member-specific data like addresses, phones, emails, and legal representatives.
- **CRUD Operations**: Perform CRUD operations on 'people' data.
- **Certificate Generation**: Generate and download certificates for members.
- **CORS Support**: Configured with CORS to allow resource sharing from specified origins.
- **Logging and Middleware**: Custom request handling and logging.



## How to run

```bash

# Install dependencies
uv sync

# Run the app (available at http://localhost:5000/...)
make run OR uv run main.py

# Alternatively use the CLI entrypoints
python -m people_api api
# Update workspace groups
python -m people_api update_workspace_groups
# Start the SQS/SNS handler
python -m people_api sqs_handler

```

## Dumping a new version of the db

```bash
pg_dump --verbose --host=IP --port=5432 --username=mensa_root --format=plain --compress=0 --file dump.sql --no-owner --no-acl -n "public" mensa
```
Then erase the line that creates the schema public. Do not let pre-commit run on it
