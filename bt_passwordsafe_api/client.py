"""
Client for interacting with the Password Safe API.
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

import requests

from bt_passwordsafe_api.exceptions import BeyondTrustApiException, BeyondTrustAuthenticationException
from bt_passwordsafe_api.models.authentication_result import AuthenticationResult
from bt_passwordsafe_api.models.managed_account import ManagedAccount
from bt_passwordsafe_api.models.managed_password import ManagedPassword
from bt_passwordsafe_api.models.managed_system import ManagedSystem
from bt_passwordsafe_api.models.password_request import PasswordRequest
from bt_passwordsafe_api.models.password_request_result import PasswordRequestResult
from bt_passwordsafe_api.models.password_safe_options import PasswordSafeOptions


class PasswordSafeClient:
    """
    Client for interacting with the Password Safe API.
    """

    def __init__(self, options: PasswordSafeOptions, logger: Optional[logging.Logger] = None):
        """
        Initialize a new instance of the PasswordSafeClient class.
        
        Args:
            options (PasswordSafeOptions): The Password Safe options.
            logger (logging.Logger, optional): The logger.
        """
        self._options = options
        self._logger = logger
        self._auth_result = None
        self._auth_lock = threading.Lock()
        
        # Validate the options
        self._options.validate()
        
        # Create a session for connection pooling
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Configure the timeout
        self._timeout = options.timeout_seconds

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        
        Returns:
            PasswordSafeClient: The client instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.
        
        Args:
            exc_type: The exception type.
            exc_val: The exception value.
            exc_tb: The exception traceback.
        """
        self.close()

    def close(self):
        """
        Close the client and release resources.
        """
        if self._session:
            self._session.close()
            self._session = None

    def authenticate(self) -> AuthenticationResult:
        """
        Authenticates with the Password Safe API.
        
        Returns:
            AuthenticationResult: Authentication result.
            
        Raises:
            BeyondTrustAuthenticationException: If authentication fails.
        """
        with self._auth_lock:
            # Check if we already have a valid token
            if self._auth_result and not self._auth_result.is_expired:
                if self._logger:
                    self._logger.info("Using existing authentication token")
                return self._auth_result

            if self._logger:
                self._logger.info("Authenticating with Password Safe API")

            # Choose the authentication method based on the options
            if self._options.use_oauth:
                return self._authenticate_with_oauth()

            # Fall back to API key authentication
            return self._authenticate_with_api_key()

    def _authenticate_with_api_key(self) -> AuthenticationResult:
        """
        Authenticates with the Password Safe API using an API key.
        
        Returns:
            AuthenticationResult: Authentication result.
            
        Raises:
            BeyondTrustAuthenticationException: If authentication fails.
        """
        # Set the API key in the request header
        auth_header = f"PS-Auth key={self._options.api_key}; runas={self._options.run_as_username}"
        
        # Only add password if it's provided
        if self._options.run_as_password:
            auth_header += f"; pwd=[{self._options.run_as_password}]"
            
        self._session.headers.update({'Authorization': auth_header})

        # Make a simple request to verify the API key works
        try:
            response = self._session.get(f"{self._options.base_url}/Auth", timeout=self._timeout)
            response.raise_for_status()
        except requests.RequestException as ex:
            raise BeyondTrustAuthenticationException(f"API key authentication failed: {str(ex)}", ex)

        if self._logger:
            self._logger.info("Successfully authenticated with API key")

        # Create a simple AuthenticationResult for API key authentication
        self._auth_result = AuthenticationResult(
            access_token=self._options.api_key,
            token_type="PS-Auth",
            expires_in=3600  # Default to 1 hour
        )

        return self._auth_result

    def _authenticate_with_oauth(self) -> AuthenticationResult:
        """
        Authenticates with the Password Safe API using OAuth.
        
        Returns:
            AuthenticationResult: Authentication result.
            
        Raises:
            BeyondTrustAuthenticationException: If authentication fails.
        """
        # Clear any existing Authorization header
        if 'Authorization' in self._session.headers:
            del self._session.headers['Authorization']

        # Prepare the form data for OAuth token request
        form_data = {
            'grant_type': 'client_credentials',
            'client_id': self._options.oauth_client_id,
            'client_secret': self._options.oauth_client_secret
        }

        try:
            # Make the OAuth token request
            response = self._session.post(
                f"{self._options.base_url}/Auth/Connect/Token",
                data=form_data,
                timeout=self._timeout,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            auth_data = response.json()
        except requests.RequestException as ex:
            raise BeyondTrustAuthenticationException(f"OAuth authentication failed: {str(ex)}", ex)
        except json.JSONDecodeError as ex:
            raise BeyondTrustAuthenticationException("Failed to parse authentication response", ex)

        # Create the authentication result
        self._auth_result = AuthenticationResult(
            access_token=auth_data.get('access_token'),
            token_type=auth_data.get('token_type'),
            expires_in=int(auth_data.get('expires_in', 0)),
            refresh_token=auth_data.get('refresh_token')
        )

        # Set the authorization header for subsequent requests
        self._session.headers.update({
            'Authorization': f"{self._auth_result.token_type} {self._auth_result.access_token}"
        })

        # Additional step: Sign into the app using the obtained access token
        try:
            sign_in_response = self._session.post(
                f"{self._options.base_url}/Auth/SignAppIn",
                timeout=self._timeout
            )
            sign_in_response.raise_for_status()
        except requests.RequestException as ex:
            raise BeyondTrustAuthenticationException(f"SignAppIn failed: {str(ex)}", ex)

        if self._logger:
            self._logger.info("Successfully signed into the app using OAuth token")

        return self._auth_result

    def _ensure_authenticated(self):
        """
        Ensures the client is authenticated before making API calls.
        
        Raises:
            BeyondTrustAuthenticationException: If authentication fails.
        """
        if not self._auth_result or self._auth_result.is_expired:
            self.authenticate()

    def get_managed_account_password_by_id(self, managed_account_id: str) -> ManagedPassword:
        """
        Gets a managed password by account ID.
        
        Args:
            managed_account_id (str): The ID of the managed account.
            
        Returns:
            ManagedPassword: Managed password.
            
        Raises:
            ValueError: If managed_account_id is None or empty.
            BeyondTrustApiException: If the API request fails.
        """
        if not managed_account_id:
            raise ValueError("Managed account ID cannot be null or empty")

        self._ensure_authenticated()

        if self._logger:
            self._logger.info(f"Retrieving managed account password by ID: {managed_account_id}")

        # First get the managed account details
        account = self.get_managed_account_by_id(managed_account_id)

        try:
            # Create a password request
            request = PasswordRequest(
                system_id=account.managed_system_id,
                account_id=account.managed_account_id,
                duration_minutes=self._options.default_password_duration,
                reason="API Password Request"
            )

            # Request the password
            request_result = self.create_password_request(request)

            # Get the password using the request ID
            try:
                response = self._session.get(
                    f"{self._options.base_url}/Credentials/{request_result.request_id}",
                    timeout=self._timeout
                )
                response.raise_for_status()
                content = response.text
            except requests.RequestException as ex:
                raise BeyondTrustApiException(f"Failed to get password: {str(ex)}", ex)

            try:
                # First try to parse as a complex object
                password_data = json.loads(content)
                password = ManagedPassword(
                    password=password_data.get('Password', ''),
                    request_id=request_result.request_id,
                    account_id=account.managed_account_id,
                    system_id=account.managed_system_id,
                    expiration_date=request_result.expiration_date
                )
                return password
            except json.JSONDecodeError:
                # If complex object deserialization fails, try parsing as a simple password string
                try:
                    # The API might just return the password as a plain string
                    raw_password = content.strip('"')
                    password = ManagedPassword(
                        password=raw_password,
                        request_id=request_result.request_id,
                        account_id=account.managed_account_id,
                        system_id=account.managed_system_id,
                        expiration_date=request_result.expiration_date
                    )
                    return password
                except Exception as ex:
                    # If all parsing attempts fail, throw an exception
                    raise BeyondTrustApiException(f"Failed to parse password response: {content}", ex)

        except BeyondTrustApiException as ex:
            # Special handling for 409 Conflict errors
            if "409" in str(ex):
                if self._logger:
                    self._logger.warning(f"Conflict detected when retrieving password for account ID: {managed_account_id}. Attempting to find existing request.")
                
                # Try to find an existing active request for this account
                existing_request = self._get_existing_request(str(account.managed_account_id))
                
                if existing_request:
                    if self._logger:
                        self._logger.info(f"Found existing request ID: {existing_request.request_id} for account ID: {managed_account_id}. Retrieving password.")
                    
                    # Get the password using the existing request ID
                    try:
                        response = self._session.get(
                            f"{self._options.base_url}/Credentials/{existing_request.request_id}",
                            timeout=self._timeout
                        )
                        response.raise_for_status()
                        content = response.text
                    except requests.RequestException as req_ex:
                        raise BeyondTrustApiException(f"Failed to get password with existing request ID {existing_request.request_id}: {str(req_ex)}", req_ex)
                    
                    try:
                        # Try to parse as a complex object first
                        password_data = json.loads(content)
                        password = ManagedPassword(
                            password=password_data.get('Password', ''),
                            request_id=existing_request.request_id,
                            account_id=account.managed_account_id,
                            system_id=account.managed_system_id,
                            expiration_date=existing_request.expiration_date
                        )
                        return password
                    except json.JSONDecodeError:
                        # If complex object deserialization doesn't return a valid object, try parsing as a simple string
                        raw_password = content.strip('"')
                        return ManagedPassword(
                            password=raw_password,
                            request_id=existing_request.request_id,
                            account_id=account.managed_account_id,
                            system_id=account.managed_system_id,
                            expiration_date=existing_request.expiration_date
                        )
                    except Exception as parse_ex:
                        raise BeyondTrustApiException(f"Failed to parse password response from existing request: {content}", parse_ex)
            
            # If we couldn't find an existing request, rethrow the original exception
            raise

    def get_managed_account_password_by_name(self, account_name: str, system_name: Optional[str] = None, 
                                            domain_name: Optional[str] = None, is_domain_linked: bool = False) -> ManagedPassword:
        """
        Gets a managed password by account name.
        
        Args:
            account_name (str): Name of the managed account.
            system_name (str, optional): Name of the managed system (required if is_domain_linked is False).
            domain_name (str, optional): Name of the domain (required if is_domain_linked is True).
            is_domain_linked (bool, optional): Whether the account is domain-linked (True) or local (False).
            
        Returns:
            ManagedPassword: Managed password.
            
        Raises:
            ValueError: If required parameters are missing.
            BeyondTrustApiException: If the API request fails.
        """
        # Get the managed account details first
        account = self.get_managed_account_by_name(account_name, system_name, domain_name, is_domain_linked)

        # Now that we have the account ID, get the password
        return self.get_managed_account_password_by_id(str(account.managed_account_id))

    def get_managed_account_password_by_request_id(self, request_id: str) -> ManagedPassword:
        """
        Gets a managed password by request ID.
        
        Args:
            request_id (str): The ID of the password request.
            
        Returns:
            ManagedPassword: Managed password.
            
        Raises:
            ValueError: If request_id is None or empty.
            BeyondTrustApiException: If the API request fails.
        """
        if not request_id:
            raise ValueError("Request ID cannot be null or empty")

        self._ensure_authenticated()

        if self._logger:
            self._logger.info(f"Retrieving managed account password by request ID: {request_id}")

        # Get the password using the request ID
        try:
            response = self._session.get(
                f"{self._options.base_url}/Credentials/{request_id}",
                timeout=self._timeout
            )
            response.raise_for_status()
            content = response.text
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to get password with request ID {request_id}: {str(ex)}", ex)

        try:
            # First try to parse as a complex object
            password_data = json.loads(content)
            password = ManagedPassword(
                password=password_data.get('Password', ''),
                request_id=request_id,
                # Account ID and System ID are not known when retrieving by request ID
                account_id=None,
                system_id=None,
                expiration_date=None
            )
            return password
        except json.JSONDecodeError:
            # If complex object deserialization fails, try parsing as a simple password string
            try:
                # The API might just return the password as a plain string
                raw_password = content.strip('"')
                password = ManagedPassword(
                    password=raw_password,
                    request_id=request_id,
                    # Account ID and System ID are not known when retrieving by request ID
                    account_id=None,
                    system_id=None,
                    expiration_date=None
                )
                return password
            except Exception as ex:
                # If all parsing attempts fail, throw an exception
                raise BeyondTrustApiException(f"Failed to parse password response: {content}", ex)

    def get_managed_account_by_name(self, account_name: str, system_name: Optional[str] = None, 
                                   domain_name: Optional[str] = None, is_domain_linked: bool = False) -> ManagedAccount:
        """
        Gets a managed account by name.
        
        Args:
            account_name (str): Name of the managed account.
            system_name (str, optional): Name of the managed system (required if is_domain_linked is False).
            domain_name (str, optional): Name of the domain (required if is_domain_linked is True).
            is_domain_linked (bool, optional): Whether the account is domain-linked (True) or local (False).
            
        Returns:
            ManagedAccount: Managed account.
            
        Raises:
            ValueError: If required parameters are missing.
            BeyondTrustApiException: If the API request fails.
        """
        if not account_name:
            raise ValueError("Account name cannot be null or empty")

        if is_domain_linked:
            if not domain_name:
                raise ValueError("Domain name is required when is_domain_linked is True")
        else:
            if not system_name:
                raise ValueError("System name is required when is_domain_linked is False")

        self._ensure_authenticated()

        if self._logger:
            self._logger.info(f"Retrieving managed account by name: {account_name}")

        # Build the query parameters
        query_params = {}

        if is_domain_linked:
            # For domain-linked accounts, format is accountname=domain\\accountName
            query_params['accountname'] = f"{domain_name}\\{account_name}"
            query_params['type'] = 'domainlinked'
        else:
            # For local accounts, use systemName and accountName separately
            query_params['systemName'] = system_name
            query_params['accountName'] = account_name

        # Get the managed account details
        try:
            response = self._session.get(
                f"{self._options.base_url}/ManagedAccounts",
                params=query_params,
                timeout=self._timeout
            )
            response.raise_for_status()
            content = response.json()
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to retrieve managed account: {str(ex)}", ex)
        except json.JSONDecodeError as ex:
            raise BeyondTrustApiException("Failed to parse managed account response", ex)

        try:
            # The API returns a single object when both systemName and accountName are provided
            # or when a domain account is specified with domain\\accountName format
            account = ManagedAccount.from_dict(content)

            # If AccountId is populated but ManagedAccountId is not, copy the value
            if account.account_id > 0 and account.managed_account_id == 0:
                account.managed_account_id = account.account_id

            # If SystemId is populated but ManagedSystemId is not, copy the value
            if account.system_id > 0 and account.managed_system_id == 0:
                account.managed_system_id = account.system_id

            return account
        except Exception as ex:
            raise BeyondTrustApiException(f"Failed to parse managed account: {str(ex)}", ex)

    def get_managed_account_by_id(self, managed_account_id: str) -> ManagedAccount:
        """
        Gets a managed account by ID.
        
        Args:
            managed_account_id (str): The ID of the managed account.
            
        Returns:
            ManagedAccount: Managed account.
            
        Raises:
            ValueError: If managed_account_id is None or empty.
            BeyondTrustApiException: If the API request fails.
        """
        if not managed_account_id:
            raise ValueError("Managed account ID cannot be null or empty")

        self._ensure_authenticated()

        if self._logger:
            self._logger.info(f"Retrieving managed account by ID: {managed_account_id}")

        try:
            response = self._session.get(
                f"{self._options.base_url}/ManagedAccounts/{managed_account_id}",
                timeout=self._timeout
            )
            response.raise_for_status()
            content = response.json()
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to retrieve managed account: {str(ex)}", ex)
        except json.JSONDecodeError as ex:
            raise BeyondTrustApiException("Failed to parse managed account response", ex)

        try:
            account = ManagedAccount.from_dict(content)

            # If AccountId is populated but ManagedAccountId is not, copy the value
            if account.account_id > 0 and account.managed_account_id == 0:
                account.managed_account_id = account.account_id

            # If SystemId is populated but ManagedSystemId is not, copy the value
            if account.system_id > 0 and account.managed_system_id == 0:
                account.managed_system_id = account.system_id

            return account
        except Exception as ex:
            raise BeyondTrustApiException(f"Failed to parse managed account: {str(ex)}", ex)

    def get_managed_accounts(self, system_id: Optional[str] = None, account_name: Optional[str] = None) -> List[ManagedAccount]:
        """
        Gets a list of managed accounts.
        
        Args:
            system_id (str, optional): Optional system ID filter.
            account_name (str, optional): Optional account name filter (requires system_id to be specified).
            
        Returns:
            List[ManagedAccount]: List of managed accounts.
            
        Raises:
            ValueError: If account_name is specified but system_id is not.
            BeyondTrustApiException: If the API request fails.
        """
        if account_name and not system_id:
            raise ValueError("system_id is required when account_name is specified")

        self._ensure_authenticated()

        if self._logger:
            self._logger.info("Retrieving managed accounts")

        # Build the query parameters
        query_params = {}
        if system_id:
            query_params['systemId'] = system_id
        if account_name:
            query_params['accountName'] = account_name

        # Get the managed accounts
        try:
            response = self._session.get(
                f"{self._options.base_url}/ManagedAccounts",
                params=query_params,
                timeout=self._timeout
            )
            response.raise_for_status()
            content = response.json()
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to retrieve managed accounts: {str(ex)}", ex)
        except json.JSONDecodeError as ex:
            raise BeyondTrustApiException("Failed to parse managed accounts response", ex)

        try:
            # If we specified both systemId and accountName, we might get a single object instead of an array
            if isinstance(content, dict) and not isinstance(content, list):
                return [ManagedAccount.from_dict(content)]

            # Otherwise, we should have an array of accounts
            return [ManagedAccount.from_dict(account_data) for account_data in content]
        except Exception as ex:
            raise BeyondTrustApiException(f"Failed to parse managed accounts: {str(ex)}", ex)

    def get_managed_systems(self, system_id: Optional[str] = None) -> List[ManagedSystem]:
        """
        Gets a list of managed systems.
        
        Args:
            system_id (str, optional): Optional system ID to retrieve a specific managed system.
            
        Returns:
            List[ManagedSystem]: List of managed systems.
            
        Raises:
            BeyondTrustApiException: If the API request fails.
        """
        self._ensure_authenticated()

        if self._logger:
            self._logger.info("Retrieving managed systems")

        # Build the URL
        url = f"{self._options.base_url}/ManagedSystems"
        if system_id:
            url = f"{url}/{system_id}"

        # Get the managed systems
        try:
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()
            content = response.json()
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to retrieve managed systems: {str(ex)}", ex)
        except json.JSONDecodeError as ex:
            raise BeyondTrustApiException("Failed to parse managed systems response", ex)

        try:
            # If we specified a systemId, we might get a single object instead of an array
            if isinstance(content, dict) and not isinstance(content, list):
                return [ManagedSystem.from_dict(content)]

            # Otherwise, we should have an array of systems
            return [ManagedSystem.from_dict(system_data) for system_data in content]
        except Exception as ex:
            raise BeyondTrustApiException(f"Failed to parse managed systems: {str(ex)}", ex)

    def create_password_request(self, request: PasswordRequest) -> PasswordRequestResult:
        """
        Creates a password request.
        
        Args:
            request (PasswordRequest): The password request details.
            
        Returns:
            PasswordRequestResult: Password request result.
            
        Raises:
            ValueError: If request is None.
            BeyondTrustApiException: If the API request fails.
        """
        if not request:
            raise ValueError("Request cannot be null")

        self._ensure_authenticated()

        if self._logger:
            self._logger.info(f"Creating password request for account ID: {request.account_id}")

        # Convert the request to a dictionary for serialization
        request_data = request.to_dict()

        # Create the password request
        try:
            response = self._session.post(
                f"{self._options.base_url}/Requests",
                json=request_data,
                timeout=self._timeout
            )
            response.raise_for_status()
            content = response.json()
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to create password request: {str(ex)}", ex)
        except json.JSONDecodeError as ex:
            raise BeyondTrustApiException("Failed to parse password request response", ex)

        try:
            # Parse the response into a PasswordRequestResult
            return PasswordRequestResult.from_dict(content)
        except Exception as ex:
            raise BeyondTrustApiException(f"Failed to parse password request result: {str(ex)}", ex)

    def _get_existing_request(self, account_id: str) -> Optional[PasswordRequestResult]:
        """
        Gets an existing active request for the specified account ID.
        
        Args:
            account_id (str): The account ID to check for existing requests.
            
        Returns:
            Optional[PasswordRequestResult]: The existing request if found, None otherwise.
            
        Raises:
            BeyondTrustApiException: If the API request fails.
        """
        if not account_id:
            return None

        self._ensure_authenticated()

        if self._logger:
            self._logger.info(f"Checking for existing requests for account ID: {account_id}")

        # Get active requests for the account
        try:
            response = self._session.get(
                f"{self._options.base_url}/Requests",
                params={'accountId': account_id, 'state': 'active'},
                timeout=self._timeout
            )
            response.raise_for_status()
            content = response.json()
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to check for existing requests: {str(ex)}", ex)
        except json.JSONDecodeError as ex:
            raise BeyondTrustApiException("Failed to parse existing requests response", ex)

        try:
            # If we have any active requests, return the first one
            if content and isinstance(content, list) and len(content) > 0:
                return PasswordRequestResult.from_dict(content[0])
            return None
        except Exception as ex:
            raise BeyondTrustApiException(f"Failed to parse existing requests: {str(ex)}", ex)

    def check_in_password(self, request_id: str, reason: Optional[str] = None) -> bool:
        """
        Checks in a password that was previously checked out.
        
        Args:
            request_id (str): The ID of the password request.
            reason (str, optional): Optional reason for checking in the password.
            
        Returns:
            bool: True if successful.
            
        Raises:
            ValueError: If request_id is None or empty.
            BeyondTrustApiException: If the API request fails.
        """
        if not request_id:
            raise ValueError("Request ID cannot be null or empty")

        self._ensure_authenticated()

        if self._logger:
            self._logger.info(f"Checking in password for request ID: {request_id}")

        # Prepare the check-in data
        check_in_data = {'Reason': reason} if reason else {}

        # Check in the password
        try:
            response = self._session.put(
                f"{self._options.base_url}/Requests/{request_id}/CheckIn",
                json=check_in_data,
                timeout=self._timeout
            )
            response.raise_for_status()
            return True
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to check in password: {str(ex)}", ex)

    def sign_out(self) -> bool:
        """
        Signs out the current user session.
        
        Returns:
            bool: True if successful.
            
        Raises:
            BeyondTrustApiException: If the API request fails.
        """
        if not self._auth_result:
            return True  # Already signed out

        if self._logger:
            self._logger.info("Signing out")

        try:
            response = self._session.post(
                f"{self._options.base_url}/Auth/SignOut",
                timeout=self._timeout
            )
            response.raise_for_status()
            
            # Clear the authentication result
            self._auth_result = None
            
            return True
        except requests.RequestException as ex:
            raise BeyondTrustApiException(f"Failed to sign out: {str(ex)}", ex)
