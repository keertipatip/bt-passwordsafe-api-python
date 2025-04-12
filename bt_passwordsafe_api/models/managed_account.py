"""
Managed account model for the Password Safe API.
"""

class ManagedAccount:
    """
    Represents a managed account in Password Safe.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a new instance of the ManagedAccount class.
        
        Args:
            **kwargs: Arbitrary keyword arguments to initialize the properties.
        """
        # Primary identifiers
        self.managed_account_id = kwargs.get('managed_account_id', 0)
        self.account_id = kwargs.get('account_id', 0)
        self.managed_system_id = kwargs.get('managed_system_id', 0)
        self.system_id = kwargs.get('system_id', 0)
        
        # Account details
        self.account_name = kwargs.get('account_name', '')
        self.domain_name = kwargs.get('domain_name', '')
        self.system_name = kwargs.get('system_name', '')
        self.account_type = kwargs.get('account_type', '')
        self.platform_id = kwargs.get('platform_id', 0)
        self.platform_name = kwargs.get('platform_name', '')
        
        # Status and properties
        self.is_domain_linked = kwargs.get('is_domain_linked', False)
        self.is_service_account = kwargs.get('is_service_account', False)
        self.is_suspended = kwargs.get('is_suspended', False)
        self.last_change_date = kwargs.get('last_change_date')
        self.next_change_date = kwargs.get('next_change_date')
        self.last_change_result = kwargs.get('last_change_result', 0)
        
        # Access control
        self.managed_by_user_id = kwargs.get('managed_by_user_id', 0)
        self.managed_by_user_name = kwargs.get('managed_by_user_name', '')
        self.managed_by_group_id = kwargs.get('managed_by_group_id', 0)
        self.managed_by_group_name = kwargs.get('managed_by_group_name', '')
        self.managed_by_team_id = kwargs.get('managed_by_team_id', 0)
        self.managed_by_team_name = kwargs.get('managed_by_team_name', '')
        
        # Additional properties
        self.description = kwargs.get('description', '')
        self.properties = kwargs.get('properties', {})
    
    def __str__(self):
        """
        Returns a string representation of the managed account.
        
        Returns:
            str: A string representation of the managed account.
        """
        return f"{self.account_name} (ID: {self.managed_account_id}) on {self.system_name}"
    
    @classmethod
    def from_dict(cls, data):
        """
        Creates a ManagedAccount instance from a dictionary.
        
        Args:
            data (dict): The dictionary containing the managed account data.
            
        Returns:
            ManagedAccount: A new ManagedAccount instance.
        """
        # Convert snake_case keys to camelCase for compatibility with API response
        converted_data = {}
        for key, value in data.items():
            # Convert camelCase or PascalCase to snake_case
            snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            converted_data[snake_key] = value
        
        # Handle special cases where API property names don't match our model
        if 'managed_account_id' not in converted_data and 'account_id' in converted_data:
            converted_data['managed_account_id'] = converted_data['account_id']
        
        if 'managed_system_id' not in converted_data and 'system_id' in converted_data:
            converted_data['managed_system_id'] = converted_data['system_id']
        
        return cls(**converted_data)
