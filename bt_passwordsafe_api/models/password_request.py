"""
Password request model for the Password Safe API.
"""

class PasswordRequest:
    """
    Represents a password request to the Password Safe API.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a new instance of the PasswordRequest class.
        
        Args:
            **kwargs: Arbitrary keyword arguments to initialize the properties.
        """
        self.system_id = kwargs.get('system_id', 0)
        self.account_id = kwargs.get('account_id', 0)
        self.duration_minutes = kwargs.get('duration_minutes', 60)
        self.reason = kwargs.get('reason', 'API Password Request')
        self.conflict_option = kwargs.get('conflict_option', 'reuse')
        self.ticket_system_id = kwargs.get('ticket_system_id')
        self.ticket_number = kwargs.get('ticket_number')
        self.access_type = kwargs.get('access_type', 'view')
    
    def to_dict(self):
        """
        Converts the password request to a dictionary for API requests.
        
        Returns:
            dict: A dictionary representation of the password request.
        """
        # Convert snake_case keys to PascalCase for API compatibility
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                # Convert snake_case to PascalCase
                pascal_key = ''.join(word.capitalize() for word in key.split('_'))
                # Ensure first letter is capital (PascalCase)
                result[pascal_key] = value
        
        return result
