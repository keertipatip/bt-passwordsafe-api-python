"""
Exception thrown when an error occurs while communicating with the BeyondTrust Password Safe API.
"""

class BeyondTrustApiException(Exception):
    """
    Exception thrown when an error occurs while communicating with the BeyondTrust Password Safe API.
    """
    
    def __init__(self, message=None, inner_exception=None):
        """
        Initialize a new instance of the BeyondTrustApiException class.
        
        Args:
            message (str, optional): The message that describes the error.
            inner_exception (Exception, optional): The exception that is the cause of the current exception.
        """
        if message is None:
            message = "An error occurred while communicating with the BeyondTrust Password Safe API"
            
        super().__init__(message)
        self.inner_exception = inner_exception
