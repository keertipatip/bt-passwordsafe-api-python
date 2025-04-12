"""
BT.PasswordSafe.API

A Python package for interacting with BeyondTrust Password Safe API. This package provides a simple and intuitive 
interface for retrieving passwords, managed accounts and managed systems from BeyondTrust Password Safe.
"""

from bt_passwordsafe_api.client import PasswordSafeClient
from bt_passwordsafe_api.models.authentication_result import AuthenticationResult
from bt_passwordsafe_api.models.managed_account import ManagedAccount
from bt_passwordsafe_api.models.managed_password import ManagedPassword
from bt_passwordsafe_api.models.managed_system import ManagedSystem
from bt_passwordsafe_api.models.password_request import PasswordRequest
from bt_passwordsafe_api.models.password_request_result import PasswordRequestResult
from bt_passwordsafe_api.models.password_safe_options import PasswordSafeOptions

__version__ = '1.0.0'
