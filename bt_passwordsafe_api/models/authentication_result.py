"""
Authentication result model for the Password Safe API.
"""

from datetime import datetime, timedelta

class AuthenticationResult:
    """
    Authentication result from the Password Safe API.
    """
    
    def __init__(self, access_token=None, token_type=None, expires_in=0, refresh_token=None):
        """
        Initialize a new instance of the AuthenticationResult class.
        
        Args:
            access_token (str): The access token.
            token_type (str): The token type.
            expires_in (int): The number of seconds until the token expires.
            refresh_token (str): The refresh token.
        """
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.issued_at = datetime.utcnow()
    
    @property
    def expires_at(self):
        """
        Gets the date and time when the token expires.
        
        Returns:
            datetime: The expiration date and time.
        """
        return self.issued_at + timedelta(seconds=self.expires_in)
    
    @property
    def is_expired(self):
        """
        Gets a value indicating whether the token is expired.
        
        Returns:
            bool: True if the token is expired; otherwise, False.
        """
        # Consider the token expired if it's within 5 minutes of expiration
        return datetime.utcnow() + timedelta(minutes=5) >= self.expires_at
