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

### App Group Endpoints
- GET `/get_can_participate`: Get groups that the member can participate in
- GET `/get_participate_in`: Get groups that the member is participating in
- GET `/get_pending_requests`: Get pending group join requests
- GET `/get_failed_requests`: Get failed group join requests

### Other Endpoints
- POST `/create_user/`: Create a new user in Google Workspace.
- GET `/download_certificate.png`: Generate and download a certificate.

## IAM Endpoints

#### **POST**
- `/create_role/` - Create a new role
- `/create_group/` - Create a new group
- `/create_permission/` - Create a new permission
- `/add_role_to_member/` - Add role to member
- `/add_group_to_member/` - Add group to member
- `/add_permission_to_role/` - Add permission to role
- `/add_permission_to_group/` - Add permission to group

#### **GET**
- `/roles/` - Get roles for member
- `/groups/` - Get groups for member
- `/members/role/` - Get members with specific role
- `/members/group/` - Get members in specific group
- `/role_permissions/` - Get permissions for role
- `/group_permissions/` - Get permissions for group

#### **PATCH**
- `/update_role/` - Update role
- `/update_group/` - Update group
- `/update_permission/` - Update permission

#### **DELETE**
- `/remove_role_from_member/` - Remove role from member
- `/remove_group_from_member/` - Remove group from member
- `/remove_permission_from_role/` - Remove permission from role
- `/remove_permission_from_group/` - Remove permission from group
- `/delete_role/` - Delete role
- `/delete_group/` - Delete group
- `/delete_permission/` - Delete permission


## Requirements

- Python >= 3.7
- Requirements listed on [pyproject.toml](pyproject.toml)

## How to run

```bash

# Install dependencies
uv sync

# Run the app (available at http://localhost:5000/...)
make run OR uv run main.py

```

## Dumping a new version of the db

```bash
pg_dump --verbose --host=IP --port=5432 --username=mensa_root --format=plain --compress=0 --file dump.sql --no-owner --no-acl -n "public" mensa
```
Then erase the line that creates the schema public. Do not let pre-commit run on it
