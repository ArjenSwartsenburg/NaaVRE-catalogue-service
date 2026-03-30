# Testing Conda Environments API with Bruno

## Overview
Bruno is an API testing tool used in the NaaVRE catalogue service. The conda-environments collection contains ready-to-use tests for creating, listing, and managing conda environments.

## Complete Test Workflow

### Option 1: Full End-to-End Test (Recommended for First Time)
This tests the complete file upload and environment creation flow:

**Execution Order:**
1. **upload-flow/presign-env-tar.bru** - Request S3 upload URL for tar file
   - Stores `envTarKey` and `envTarUrl` as variables

2. **upload-flow/presign-requirements.bru** - Request S3 upload URL for requirements file
   - Stores `requirementsKey` and `requirementsUrl` as variables

3. **upload-flow/upload-env-tar.bru** - Upload tar file content to S3
   - Uses `envTarUrl` to PUT the file
   - Validates HTTP 200 response

4. **upload-flow/upload-requirements.bru** - Upload requirements file to S3
   - Uses `requirementsUrl` to PUT the file
   - Validates HTTP 200 response

5. **Create conda environment.bru** - Create the environment asset
   - Uses `envTarKey` and `requirementsKey` from presign responses
   - Includes metadata: environment_name, python_version, package_count, created_date
   - Validates HTTP 201 response
   - Extracts `condaEnvUUID` from response URL for next steps

### Option 2: Quick CRUD Tests (After Environment Created)
Test environment operations without re-creating:

1. **List.bru** - List all environments
   - GET /conda-environments/
   - Returns paginated list with count

2. **Retrieve.bru** - Get specific environment details
   - GET /conda-environments/{id}/
   - Shows all files and metadata

3. **Partial update.bru** - Update environment metadata
   - PATCH /conda-environments/{id}/
   - Update title, description, etc.

4. **Delete.bru** - Delete an environment
   - DELETE /conda-environments/{id}/
   - Cascades to delete all files from S3

## How to Run in Bruno

### Via Bruno GUI
1. Open Bruno application
2. Load the NaaVRE catalogue service collection
3. Navigate to **conda-environments** folder
4. **For E2E test**: Right-click `upload-flow` folder → "Run" (runs sequence in order)
5. **For specific test**: Click individual request and press "Send"
6. Check response status and tests panel for results

### What Variables Are Set
Bruno stores variables during execution that are reused in subsequent requests:

| Variable | Set By | Used By | Value |
|----------|--------|---------|-------|
| `baseUrl` | Environment | All requests | `http://localhost:8000/api` |
| `ourJWT` | Environment | All requests | JWT auth token |
| `envTarKey` | presign-env-tar | Create request | S3 key for tar file |
| `envTarUrl` | presign-env-tar | upload-env-tar | S3 presigned upload URL |
| `requirementsKey` | presign-requirements | Create request | S3 key for requirements |
| `requirementsUrl` | presign-requirements | upload-requirements | S3 presigned upload URL |
| `condaEnvUUID` | Create request | Retrieve/Update/Delete | UUID of created environment |

## Key Test Validations

### Presign Requests (200 OK)
✓ Response has `key` property (S3 object path)
✓ Response has `url` property (presigned upload URL)
✓ Both are non-null strings

### File Uploads (200 OK)
✓ HTTP 200 response from S3 presigned URL
✓ Files are stored in S3 bucket

### Create Environment (201 Created)
✓ HTTP 201 response
✓ Response includes all metadata fields
✓ `files` array has exactly 2 entries (tar + requirements)
✓ `url` property extracted for UUID
✓ File types are correctly assigned

### List Environment (200 OK)
✓ HTTP 200 response
✓ `count` property >= 0 (total environments)
✓ Pagination support

### Retrieve Environment (200 OK)
✓ HTTP 200 response
✓ Single environment details with all files
✓ File information nested under `files` array

### Update Environment (200 OK)
✓ HTTP 200 response
✓ Metadata fields updated
✓ Files remain unchanged

### Delete Environment (204 No Content)
✓ HTTP 204 response
✓ Files deleted from S3
✓ Asset removed from database

## Setting Up Environment Variables

Before running tests, ensure these variables are set in Bruno:

1. **baseUrl** - API base URL (default: `http://localhost:8000/api`)
2. **ourJWT** - Valid JWT token for authentication
   - Get from login response or Django shell: `python manage.py shell`
   - Create user and token: `from rest_framework.authtoken.models import Token`

For localhost testing:
```bash
# In Django shell
python manage.py shell
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.get(username='test-user-2')
token = Token.objects.create(user=user)
print(token.key)  # Copy this to ourJWT variable
```

## Example: Running Complete Test Flow

1. **Start Django development server**
   ```bash
   cd /home/ubuntu/NaaVRE-catalogue-service/app
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Open Bruno** and navigate to `/conda-environments/upload-flow`

3. **Click "Run Folder"** to execute in sequence:
   - presign-env-tar (seq: 1)
   - presign-requirements (seq: 2)
   - upload-env-tar (seq: 3)
   - upload-requirements (seq: 4)

4. **Navigate to parent folder** `/conda-environments`

5. **Click "Create conda environment"** (seq: 2)
   - Should see HTTP 201
   - `condaEnvUUID` variable is set

6. **Click "List"** to see all environments
   - Should see your newly created environment

7. **Click "Retrieve"** to see full details with files
   - Should show both tar and requirements files

## Troubleshooting

### "Status code is 401 (Unauthorized)"
- Check `ourJWT` variable is valid
- Verify token not expired

### "Status code is 400 (Bad Request)"
- Check required fields in request body
- Verify `baseUrl` matches your server

### "Status code is 404 (Not Found)"
- Check environment UUID in URL
- Verify request path is correct

### "Status code is 409 (Conflict)"
- File type already exists for this environment
- Delete environment and retry with new data

### Files not uploading to S3
- Check presigned URL is still valid (5 min expiry)
- Run presign requests again before upload
- Verify S3 bucket is accessible

## Next Steps

After confirming CRUD operations work:
1. Test permission/sharing system
2. Test filtering by virtual_lab
3. Test updates to metadata
4. Test file updates (replacing tar/requirements)
5. Test cascade delete (files removed from S3)
