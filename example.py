#!/usr/bin/env python3
"""
Example script demonstrating how to use the BT.PasswordSafe.API Python package.
"""

import logging
import sys
from bt_passwordsafe_api import PasswordSafeClient, PasswordSafeOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to demonstrate the BT.PasswordSafe.API package."""
    
    # Create options
    options = PasswordSafeOptions(
        # Replace with your actual values
        base_url="https://your-instance.beyondtrustcloud.com/BeyondTrust/api/public/v3/",
        api_key="your-api-key",
        run_as_username="your-username",
        run_as_password="your-password",
        # Or for OAuth:
        # use_oauth=True,
        # oauth_client_id="your-client-id",
        # oauth_client_secret="your-client-secret",
        timeout_seconds=30,
        default_password_duration=60,  # minutes
        auto_refresh_token=True
    )
    
    try:
        # Create client
        with PasswordSafeClient(options, logger) as client:
            # Authenticate
            logger.info("Authenticating with Password Safe API...")
            auth_result = client.authenticate()
            logger.info(f"Authentication successful. Token type: {auth_result.token_type}")
            logger.info(f"Token expires in: {auth_result.expires_in} seconds")
            
            # Get managed systems
            logger.info("Getting managed systems...")
            systems = client.get_managed_systems()
            logger.info(f"Found {len(systems)} managed systems")
            
            # Display first few systems
            for i, system in enumerate(systems[:5]):
                logger.info(f"System {i+1}: {system.system_name} (ID: {system.managed_system_id})")
            
            # Get managed accounts
            logger.info("Getting managed accounts...")
            accounts = client.get_managed_accounts()
            logger.info(f"Found {len(accounts)} managed accounts")
            
            # Display first few accounts
            for i, account in enumerate(accounts[:5]):
                logger.info(f"Account {i+1}: {account.account_name} on {account.system_name} (ID: {account.managed_account_id})")
            
            # Get password for a specific account
            # Uncomment and modify with actual account ID
            # account_id = "50"
            # logger.info(f"Getting password for account ID: {account_id}...")
            # password = client.get_managed_account_password_by_id(account_id)
            # logger.info(f"Retrieved password for account ID {account_id}")
            # logger.info(f"Password: {password.password[:1]}*****")  # Show only first character for security
            # logger.info(f"Request ID: {password.request_id}")
            # logger.info(f"Expires: {password.expiration_date}")
            
            # Check in the password
            # logger.info(f"Checking in password for request ID: {password.request_id}...")
            # check_in_result = client.check_in_password(password.request_id, "Example script completed")
            # logger.info(f"Check-in result: {'Success' if check_in_result else 'Failed'}")
            
            # Sign out
            logger.info("Signing out...")
            sign_out_result = client.sign_out()
            logger.info(f"Sign-out result: {'Success' if sign_out_result else 'Failed'}")
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Example completed successfully")

if __name__ == "__main__":
    main()
