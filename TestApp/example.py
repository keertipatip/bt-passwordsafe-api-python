#!/usr/bin/env python3
"""
Example script demonstrating how to use the BT.PasswordSafe.API Python package.
"""

import json
import logging
import os
import sys

# Add the parent directory to the Python path so we can import the package
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from bt_passwordsafe_api import PasswordSafeClient, PasswordSafeOptions, PasswordRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to demonstrate the BT.PasswordSafe.API package."""
    
    # Load configuration from config.json
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        logger.info(f"Loading configuration from {config_path}")
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Create options using the loaded configuration
    options = PasswordSafeOptions(
        base_url=config['PasswordSafe']['BaseUrl'],
        api_key=config['PasswordSafe']['ApiKey'],
        run_as_username=config['PasswordSafe']['RunAsUsername'],
        run_as_password=config['PasswordSafe']['RunAsPassword'],
        use_oauth=config['PasswordSafe']['UseOAuth'],
        oauth_client_id=config['PasswordSafe']['OAuthClientId'],
        oauth_client_secret=config['PasswordSafe']['OAuthClientSecret'],
        timeout_seconds=config['PasswordSafe']['TimeoutSeconds'],
        default_password_duration=config['PasswordSafe']['DefaultPasswordDuration'],
        auto_refresh_token=config['PasswordSafe']['AutoRefreshToken']
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
            
            # Get password for a specific account using test settings from config
            account_id = config['TestSettings']['AccountId']
            system_id = config['TestSettings']['SystemId']
            logger.info(f"Getting password for account ID: {account_id} on system ID: {system_id}...")
            
            # Get the password using the request
            password = client.get_managed_account_password_by_id(account_id, reason="Example script demonstration")
            logger.info(f"Retrieved password for account ID {account_id}")
            logger.info(f"Password: {password.password[:1]}*****")  # Show only first character for security
            logger.info(f"Request ID: {password.request_id}")
            logger.info(f"Expires: {password.expiration_date}")
            
            # Get password by request ID
            request_id = password.request_id  # Use the request ID from a previous request
            logger.info(f"Getting password using request ID: {request_id}...")
            password_by_request_id = client.get_managed_account_password_by_request_id(request_id, reason="Example script demonstration")
            logger.info(f"Retrieved password using request ID {request_id}")
            logger.info(f"Password: {password_by_request_id.password[:1]}*****")  # Show only first character for security
            
            # Check in the password
            logger.info(f"Checking in password for request ID: {password.request_id}...")
            check_in_result = client.check_in_password(password.request_id, "Example script completed")
            logger.info(f"Check-in result: {'Success' if check_in_result else 'Failed'}")
            
            # Sign out
            logger.info("Signing out...")
            sign_out_result = client.sign_out()
            logger.info(f"Sign-out result: {'Success' if sign_out_result else 'Failed'}")
            
            # Demonstrate the new Secret Safe functionality
            if 'SecretId' in config.get('TestSettings', {}):
                # Re-authenticate since we signed out
                logger.info("Re-authenticating to demonstrate Secret Safe functionality...")
                client.authenticate()
                
                # Get secret by ID
                secret_id = config['TestSettings']['SecretId']
                logger.info(f"Getting secret by ID: {secret_id}...")
                secret = client.get_secret_by_id(secret_id)
                if secret:
                    logger.info(f"Retrieved secret: {secret.title}")
                    logger.info(f"Secret Type: {secret.secret_type}")
                    # Don't log the actual secret value for security reasons
                    logger.info(f"Secret Value: {'*' * 8}")
                else:
                    logger.info(f"No secret found with ID: {secret_id}")
                
                # Get secret by name
                if 'SecretName' in config['TestSettings']:
                    secret_name = config['TestSettings']['SecretName']
                    logger.info(f"Getting secret by name: {secret_name}...")
                    secret = client.get_secret_by_name(secret_name)
                    if secret:
                        logger.info(f"Retrieved secret by name: {secret.title}")
                        logger.info(f"Secret ID: {secret.id}")
                        logger.info(f"Secret Type: {secret.secret_type}")
                        # Don't log the actual secret value for security reasons
                        logger.info(f"Secret Value: {'*' * 8}")
                    else:
                        logger.info(f"No secret found with name: {secret_name}")
                
                # Sign out again
                logger.info("Signing out...")
                client.sign_out()
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Example completed successfully")

if __name__ == "__main__":
    main()
