"""
Password request result model for the Password Safe API.
"""

from datetime import datetime

class PasswordRequestResult:
    """
    Represents the result of a password request to the Password Safe API.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a new instance of the PasswordRequestResult class.
        
        Args:
            **kwargs: Arbitrary keyword arguments to initialize the properties.
        """
        self.request_id = kwargs.get('request_id', '')
        self.system_id = kwargs.get('system_id', 0)
        self.account_id = kwargs.get('account_id', 0)
        self.duration_minutes = kwargs.get('duration_minutes', 60)
        self.creation_date = kwargs.get('creation_date')
        self.expiration_date = kwargs.get('expiration_date')
        self.status = kwargs.get('status', '')
        self.reason = kwargs.get('reason', '')
        self.requester_name = kwargs.get('requester_name', '')
        self.requester_id = kwargs.get('requester_id', 0)
        self.ticket_system_id = kwargs.get('ticket_system_id')
        self.ticket_number = kwargs.get('ticket_number')
        self.access_type = kwargs.get('access_type', 'view')
    
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
    
    @classmethod
    def from_dict(cls, data):
        """
        Creates a PasswordRequestResult instance from a dictionary.
        
        Args:
            data (dict): The dictionary containing the password request result data.
            
        Returns:
            PasswordRequestResult: A new PasswordRequestResult instance.
        """
        # Convert snake_case keys to camelCase for compatibility with API response
        converted_data = {}
        for key, value in data.items():
            # Convert camelCase or PascalCase to snake_case
            snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            converted_data[snake_key] = value
        
        return cls(**converted_data)
