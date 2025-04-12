"""
Configuration options for the Password Safe client.
"""

class PasswordSafeOptions:
    """
    Configuration options for the Password Safe client.
    """
    
    def __init__(self, 
                 base_url=None,
                 api_key=None,
                 run_as_username=None,
                 run_as_password=None,
                 use_oauth=False,
                 oauth_client_id=None,
                 oauth_client_secret=None,
                 timeout_seconds=30,
                 auto_refresh_token=True,
                 default_password_duration=60):
        """
        Initialize a new instance of the PasswordSafeOptions class.
        
        Args:
            base_url (str): The base URL of the Password Safe API.
                For on-premises: https://your-server/BeyondTrust/api/public/v3
                For cloud: https://your-cloud-instance-url/BeyondTrust/api/public/v3
            api_key (str): The API key configured in BeyondInsight for your application.
            run_as_username (str): The username of a BeyondInsight user that has been granted permission to use the API key.
            run_as_password (str): The RunAs user password.
            use_oauth (bool): Whether to use OAuth authentication instead of PS-Auth.
            oauth_client_id (str): The OAuth client ID (only used when use_oauth is True).
            oauth_client_secret (str): The OAuth client secret (only used when use_oauth is True).
            timeout_seconds (int): The timeout for HTTP requests in seconds.
            auto_refresh_token (bool): Whether to automatically refresh the authentication token before it expires.
            default_password_duration (int): The default duration in minutes for password requests.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.run_as_username = run_as_username
        self.run_as_password = run_as_password
        self.use_oauth = use_oauth
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.timeout_seconds = timeout_seconds
        self.auto_refresh_token = auto_refresh_token
        self.default_password_duration = default_password_duration
    
    def validate(self):
        """
        Validates the configuration options.
        
        Raises:
            ValueError: When required options are missing or invalid.
        """
        if not self.base_url:
            raise ValueError("base_url is required")
        
        if self.use_oauth:
            if not self.oauth_client_id:
                raise ValueError("oauth_client_id is required when use_oauth is True")
            
            if not self.oauth_client_secret:
                raise ValueError("oauth_client_secret is required when use_oauth is True")
        else:
            if not self.run_as_username:
                raise ValueError("run_as_username is required when use_oauth is False")
            
            if not self.api_key:
                raise ValueError("api_key is required")
