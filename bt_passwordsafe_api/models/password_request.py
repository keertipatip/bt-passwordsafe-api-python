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
                      system_id (int): The ID of the system (required).
                      account_id (int): The ID of the account.
                      duration_minutes (int): The duration in minutes for the password request.
                      reason (str): The reason for the password request.
                      conflict_option (str): The option for handling conflicts.
                      ticket_system_id (str): The ID of the ticket system.
                      ticket_number (str): The ticket number.
                      access_type (str): The type of access requested.
                      
        Raises:
            ValueError: If system_id is not provided.
        """
        # Check if system_id is provided
        if 'system_id' not in kwargs or kwargs['system_id'] is None:
            raise ValueError("system_id is required for password requests")
            
        self.system_id = kwargs['system_id']
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
