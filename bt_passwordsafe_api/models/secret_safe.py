"""
Model for a Secret Safe object.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from uuid import UUID


class SecretSafe:
    """
    Represents a Secret Safe object in Password Safe.
    """

    def __init__(
        self,
        id: Optional[UUID] = None,
        title: Optional[str] = None,
        secret_type: Optional[str] = None,
        secret_value: Optional[str] = None,
        created_date: Optional[datetime] = None,
        created_by: Optional[str] = None,
        last_modified_date: Optional[datetime] = None,
        last_modified_by: Optional[str] = None,
        folder_id: Optional[UUID] = None,
        folder_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a new instance of the SecretSafe class.
        
        Args:
            id (UUID, optional): The unique identifier of the secret.
            title (str, optional): The title of the secret.
            secret_type (str, optional): The type of the secret.
            secret_value (str, optional): The value of the secret.
            created_date (datetime, optional): The date the secret was created.
            created_by (str, optional): The user who created the secret.
            last_modified_date (datetime, optional): The date the secret was last modified.
            last_modified_by (str, optional): The user who last modified the secret.
            folder_id (UUID, optional): The ID of the folder containing the secret.
            folder_path (str, optional): The path of the folder containing the secret.
        """
        self.id = id
        self.title = title
        self.secret_type = secret_type
        self.secret_value = secret_value
        self.created_date = created_date
        self.created_by = created_by
        self.last_modified_date = last_modified_date
        self.last_modified_by = last_modified_by
        self.folder_id = folder_id
        self.folder_path = folder_path
        
        # Store any additional properties
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecretSafe':
        """
        Creates a SecretSafe object from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing the secret data.
            
        Returns:
            SecretSafe: A new SecretSafe object.
        """
        if not data:
            return cls()
            
        # Parse dates if they exist
        created_date = None
        if data.get('CreatedDate'):
            try:
                created_date = datetime.fromisoformat(data['CreatedDate'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
                
        last_modified_date = None
        if data.get('LastModifiedDate'):
            try:
                last_modified_date = datetime.fromisoformat(data['LastModifiedDate'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
                
        # Parse UUIDs if they exist
        id_value = None
        if data.get('Id'):
            try:
                id_value = UUID(data['Id'])
            except (ValueError, TypeError):
                id_value = data['Id']
                
        folder_id = None
        if data.get('FolderId'):
            try:
                folder_id = UUID(data['FolderId'])
            except (ValueError, TypeError):
                folder_id = data['FolderId']
        
        # Create the object with the parsed values
        return cls(
            id=id_value,
            title=data.get('Title'),
            secret_type=data.get('SecretType'),
            secret_value=data.get('SecretValue'),
            created_date=created_date,
            created_by=data.get('CreatedBy'),
            last_modified_date=last_modified_date,
            last_modified_by=data.get('LastModifiedBy'),
            folder_id=folder_id,
            folder_path=data.get('FolderPath'),
            # Add any additional properties as keyword arguments
            **{k: v for k, v in data.items() if k not in [
                'Id', 'Title', 'SecretType', 'SecretValue', 'CreatedDate', 'CreatedBy',
                'LastModifiedDate', 'LastModifiedBy', 'FolderId', 'FolderPath'
            ]}
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the SecretSafe object to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the SecretSafe object.
        """
        result = {
            'Id': str(self.id) if self.id else None,
            'Title': self.title,
            'SecretType': self.secret_type,
            'SecretValue': self.secret_value,
            'CreatedDate': self.created_date.isoformat() if self.created_date else None,
            'CreatedBy': self.created_by,
            'LastModifiedDate': self.last_modified_date.isoformat() if self.last_modified_date else None,
            'LastModifiedBy': self.last_modified_by,
            'FolderId': str(self.folder_id) if self.folder_id else None,
            'FolderPath': self.folder_path
        }
        
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}
