"""
Managed system model for the Password Safe API.
"""

class ManagedSystem:
    """
    Represents a managed system in Password Safe.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a new instance of the ManagedSystem class.
        
        Args:
            **kwargs: Arbitrary keyword arguments to initialize the properties.
        """
        # Primary identifiers
        self.managed_system_id = kwargs.get('managed_system_id', 0)
        self.system_id = kwargs.get('system_id', 0)
        
        # System details
        self.system_name = kwargs.get('system_name', '')
        self.asset_id = kwargs.get('asset_id', 0)
        self.asset_name = kwargs.get('asset_name', '')
        self.platform_id = kwargs.get('platform_id', 0)
        self.platform_name = kwargs.get('platform_name', '')
        self.netbios_name = kwargs.get('netbios_name', '')
        self.ip_address = kwargs.get('ip_address', '')
        self.domain_name = kwargs.get('domain_name', '')
        self.forest_name = kwargs.get('forest_name', '')
        self.fqdn = kwargs.get('fqdn', '')
        
        # Status and properties
        self.port = kwargs.get('port', 0)
        self.system_type = kwargs.get('system_type', '')
        self.is_active = kwargs.get('is_active', True)
        self.is_suspended = kwargs.get('is_suspended', False)
        self.last_scan_date = kwargs.get('last_scan_date')
        self.last_password_change_date = kwargs.get('last_password_change_date')
        
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
        Returns a string representation of the managed system.
        
        Returns:
            str: A string representation of the managed system.
        """
        return f"{self.system_name} (ID: {self.managed_system_id})"
    
    @classmethod
    def from_dict(cls, data):
        """
        Creates a ManagedSystem instance from a dictionary.
        
        Args:
            data (dict): The dictionary containing the managed system data.
            
        Returns:
            ManagedSystem: A new ManagedSystem instance.
        """
        # Convert snake_case keys to camelCase for compatibility with API response
        converted_data = {}
        for key, value in data.items():
            # Convert camelCase or PascalCase to snake_case
            snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            converted_data[snake_key] = value
        
        # Handle special cases where API property names don't match our model
        if 'managed_system_id' not in converted_data and 'system_id' in converted_data:
            converted_data['managed_system_id'] = converted_data['system_id']
        
        return cls(**converted_data)
