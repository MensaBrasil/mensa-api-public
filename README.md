Geração das imagens dos Certificados: Credito Marcos Rebello (MB 135)

## Features
- **Authentication and Security**: Utilizes Firebase token verification and secret key validation for secure access.
- **User Management**: Create and manage users in Google Workspace.
- **Member Management**: Manage member-specific data like addresses, phones, emails, and legal representatives.
- **CRUD Operations**: Perform CRUD operations on 'people' data.
- **Certificate Generation**: Generate and download certificates for members.
- **CORS Support**: Configured with CORS to allow resource sharing from specified origins.
- **Logging and Middleware**: Custom request handling and logging.


## API Endpoints
Below is a brief overview of the available API endpoints:

### Member Endpoints
- GET `/get_member_groups`: Get member groups.
- POST `/missing_fields`: Set missing fields for a member.
- PUT `/update_fb_profession/{mb}`: Update profession and Facebook URL for a member.

### Address Management
- POST `/address/{mb}`: Add an address to a member.
- PUT `/address/{mb}/{address_id}`: Update an address for a member.
- DELETE `/address/{mb}/{address_id}`: Delete an address from a member.

### Email Management
- POST `/email/{mb}`: Add an email to a member.
- PUT `/email/{mb}/{email_id}`: Update an email for a member.
- DELETE `/email/{mb}/{email_id}`: Delete an email from a member.

### People CRUD Operations
- GET `/people`: List all people.
- POST `/people`: Create a new person.
- PATCH `/people/{person_id}`: Update a person.
- DELETE `/people/{person_id}`: Delete a person.

### Other Endpoints
- POST `/create_user/`: Create a new user in Google Workspace.
- GET `/download_certificate.png`: Generate and download a certificate.



## Requirements

- Python >= 3.7
- Requirements listed on [requirements.txt](requirements.txt)
- Running MongoDB server

## How to run

```bash

# Activate venv
poetry shell

# Install requirements
poetry install

# Run the app (available at http://localhost:5000/...)
make run OR python .

```
