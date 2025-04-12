"""
Exception thrown when authentication with the BeyondTrust Password Safe API fails.
"""

from bt_passwordsafe_api.exceptions.beyond_trust_api_exception import BeyondTrustApiException

class BeyondTrustAuthenticationException(BeyondTrustApiException):
    """
    Exception thrown when authentication with the BeyondTrust Password Safe API fails.
    """
    
    def __init__(self, message=None, inner_exception=None):
        """
        Initialize a new instance of the BeyondTrustAuthenticationException class.
        
        Args:
            message (str, optional): The message that describes the error.
            inner_exception (Exception, optional): The exception that is the cause of the current exception.
        """
        if message is None:
            message = "Authentication with the BeyondTrust Password Safe API failed"
            
        super().__init__(message, inner_exception)
