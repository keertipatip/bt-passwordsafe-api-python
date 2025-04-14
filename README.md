# BT.PasswordSafe.API for Python

A Python package for interacting with BeyondTrust Password Safe API. This package provides a simple and intuitive interface for retrieving passwords, managed accounts and managed systems from BeyondTrust Password Safe.

## Features

- 🔐 **Authentication**: Support for both API Key and OAuth authentication methods
- 🔄 **Token Management**: Handles token refresh and expiration automatically
- 🔍 **Managed Accounts**: Find and manage accounts by ID, name, or system
- 🔎 **Managed Systems**: Retrieve managed systems by ID or get a complete list
- 🔑 **Password Retrieval**: Get passwords with automatic request handling and conflict resolution
- 🧩 **Error Handling**: Gracefully handles API errors including 409 Conflict scenarios
- 📝 **Detailed Logging**: Comprehensive logging for troubleshooting and auditing
- 🔐 **Secret Safe**: Access and retrieve secrets from BeyondTrust Secret Safe
- ⚡ **Full Async Support**: Complete async/await pattern implementation for all operations
- 🛡️ **Type Safety**: Type hints for all API interactions

## Installation

```bash
pip install bt-passwordsafe-api
```

## Quick Start

### Basic Usage

```python
import logging
from bt_passwordsafe_api import PasswordSafeClient, PasswordSafeOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create options
options = PasswordSafeOptions(
    base_url="https://your-instance.beyondtrustcloud.com/BeyondTrust/api/public/v3/",
    api_key="your-api-key",
    run_as_username="your-username",
    run_as_password="your-password",
    # Or for OAuth:
    # use_oauth=True,
    # oauth_client_id="your-client-id",
    # oauth_client_secret="your-client-secret",
    timeout_seconds=30,
    default_password_duration=60,  # minutes
    auto_refresh_token=True
)

# Create client
client = PasswordSafeClient(options, logger)

# Authenticate
auth_result = client.authenticate()
print(f"Token Type: {auth_result.token_type}")
print(f"Expires In: {auth_result.expires_in} seconds")

# Get password by account ID
try:
    password = client.get_managed_account_password_by_id("50", reason="API Example")
    print(f"Password: {password.password}")
    print(f"Request ID: {password.request_id}")
    print(f"Expires: {password.expiration_date}")
    
    # Get password by request ID (useful when you've already created a request)
    request_id = "12345"  # Request ID from a previous request
    password_by_request_id = client.get_managed_account_password_by_request_id(request_id, reason="API Example")
    print(f"Password: {password_by_request_id.password}")
    
    # Check in the password when done
    client.check_in_password(password.request_id, "Task completed")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Sign out when done
    client.sign_out()
```

### Using with a Context Manager

```python
from bt_passwordsafe_api import PasswordSafeClient, PasswordSafeOptions

options = PasswordSafeOptions(
    base_url="https://your-instance.beyondtrustcloud.com/BeyondTrust/api/public/v3/",
    api_key="your-api-key",
    run_as_username="your-username",
    run_as_password="your-password"
)

# Use with context manager to automatically close the session
with PasswordSafeClient(options) as client:
    # Authenticate
    client.authenticate()
    
    # Get password by account name and system name
    password = client.get_managed_account_password_by_name("admin", "DC01", reason="Context Manager Example")
    print(f"Password: {password.password}")
    
    # Check in the password when done
    client.check_in_password(password.request_id, "Task completed")
```

## Advanced Usage

### Handling Existing Requests

The SDK automatically handles cases where a password request already exists (409 Conflict). It will attempt to find and use the existing request instead of creating a new one.

```python
# This will work even if there's already an active request for this account
password = client.get_managed_account_password_by_id("50", reason="Automated Task")
```

### Using the Reason Parameter

All password retrieval methods support an optional reason parameter that allows you to document why the password is being accessed. This is useful for auditing and compliance purposes.

```python
# Get password by account ID with reason
password = client.get_managed_account_password_by_id("50", reason="Monthly Maintenance")

# Get password by account name with reason
password = client.get_managed_account_password_by_name("admin", "DC01", reason="Emergency Access")

# Get password by request ID with reason
password = client.get_managed_account_password_by_request_id("12345", reason="Scheduled Task")
```

### Retrieving Managed Accounts

```python
# Get all managed accounts
accounts = client.get_managed_accounts()
for account in accounts:
    print(f"Account: {account.account_name} (ID: {account.managed_account_id})")

# Get accounts for a specific system by system ID
system_accounts = client.get_managed_accounts("123")

# Get a specific account by system ID and account name
specific_account = client.get_managed_accounts("123", "admin")
# This returns a list with a single account if found
```

### Retrieving Managed Systems

```python
# Get all managed systems
systems = client.get_managed_systems()
for system in systems:
    print(f"System: {system.system_name} (ID: {system.managed_system_id})")

# Get a specific system by ID
specific_system = client.get_managed_systems("123")
# This returns a list with a single system if found
```

### Creating Custom Password Requests

```python
from bt_passwordsafe_api import PasswordRequest

# Create a custom password request
request = PasswordRequest(
    system_id=123,
    account_id=50,
    duration_minutes=120,  # 2 hours
    reason="Custom API request",
    conflict_option="reuse"  # Options: reuse, fail
)

# Submit the request
request_result = client.create_password_request(request)
print(f"Request ID: {request_result.request_id}")
print(f"Expires: {request_result.expiration_date}")
```

### Working with Secret Safe

```python
# Get a secret by its ID
secret_id = "12345678-1234-1234-1234-123456789012"  # UUID format
secret = client.get_secret_by_id(secret_id)
if secret:
    print(f"Secret Title: {secret.title}")
    print(f"Secret Type: {secret.secret_type}")
    print(f"Secret Value: {secret.secret_value}")

# Get a secret by its name (title)
secret_name = "Database Connection String"
secret = client.get_secret_by_name(secret_name)
if secret:
    print(f"Secret ID: {secret.id}")
    print(f"Secret Type: {secret.secret_type}")
    print(f"Secret Value: {secret.secret_value}")
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| base_url | The base URL of your BeyondTrust Password Safe API | Required |
| api_key | API key for authentication | Required for API Key auth |
| run_as_username | Username for run-as authentication | Required for API Key auth |
| run_as_password | Password for run-as authentication | Optional |
| use_oauth | Whether to use OAuth authentication | False |
| oauth_client_id | OAuth client ID | Required for OAuth auth |
| oauth_client_secret | OAuth client secret | Required for OAuth auth |
| timeout_seconds | HTTP request timeout in seconds | 30 |
| default_password_duration | Default duration for password requests in minutes | 60 |
| auto_refresh_token | Whether to automatically refresh the OAuth token | True |

## Error Handling

The package provides specific exception types for different error scenarios:

```python
from bt_passwordsafe_api.exceptions import BeyondTrustApiException, BeyondTrustAuthenticationException

try:
    # Make API calls
    client.authenticate()
    password = client.get_managed_account_password_by_id("50")
except BeyondTrustAuthenticationException as auth_ex:
    print(f"Authentication error: {auth_ex}")
except BeyondTrustApiException as api_ex:
    print(f"API error: {api_ex}")
except Exception as ex:
    print(f"Unexpected error: {ex}")
```

## Running the Example

The package includes an example script in the `TestApp` folder that demonstrates common usage patterns:

1. Navigate to the TestApp folder:
   ```bash
   cd TestApp
   ```

2. Configure your settings in `config.json`:
   ```json
   {
     "PasswordSafe": {
       "BaseUrl": "https://your-instance.beyondtrustcloud.com/BeyondTrust/api/public/v3/",
       "ApiKey": "your-api-key",
       "RunAsUsername": "your-username",
       "RunAsPassword": "your-password",
       "UseOAuth": false,
       "OAuthClientId": "",
       "OAuthClientSecret": "",
       "TimeoutSeconds": 30,
       "DefaultPasswordDuration": 60,
       "AutoRefreshToken": true
     },
     "TestSettings": {
       "SystemId": "57",
       "AccountId": "50",
       "AccountName": "test",
       "SystemName": "DC01"
     }
   }
   ```

3. Run the example script:
   ```bash
   python example.py
   ```

The example demonstrates:
- Authentication with OAuth or API Key
- Retrieving managed systems and accounts
- Creating password requests with the required system_id parameter
- Getting passwords by account ID and request ID
- Checking in passwords
- Proper error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
