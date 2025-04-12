"""
Managed password model for the Password Safe API.
"""

from datetime import datetime

class ManagedPassword:
    """
    Represents a managed password retrieved from Password Safe.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a new instance of the ManagedPassword class.
        
        Args:
            **kwargs: Arbitrary keyword arguments to initialize the properties.
        """
        self.password = kwargs.get('password', '')
        self.request_id = kwargs.get('request_id', '')
        self.account_id = kwargs.get('account_id', 0)
        self.system_id = kwargs.get('system_id', 0)
        self.expiration_date = kwargs.get('expiration_date')
    
    def __str__(self):
        """
        Returns a string representation of the managed password.
        
        Returns:
            str: A string representation of the managed password.
        """
        # Never include the actual password in string representation for security
        return f"Password for account ID: {self.account_id} (Request ID: {self.request_id})"
    
    @property
    def is_expired(self):
        """
        Gets a value indicating whether the password request has expired.
        
        Returns:
            bool: True if the password request has expired; otherwise, False.
        """
        if not self.expiration_date:
            return True
        
        if isinstance(self.expiration_date, str):
            try:
                expiration = datetime.fromisoformat(self.expiration_date.replace('Z', '+00:00'))
            except ValueError:
                # If we can't parse the date, assume it's expired
                return True
        else:
            expiration = self.expiration_date
            
        return datetime.utcnow() > expiration
