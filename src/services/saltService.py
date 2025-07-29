from typing import Optional, List, Dict, Any
from src.cyrpto.salt import Salt
from src.model.model_salt import ModelSalt
from src.repository.saltRepository import SaltRepository
from src.utils.enviroment_variable import read_env_file
import logging


class SaltService:
    """
    Service layer for salt management operations.
    Handles business logic for salt generation, validation, and persistence.
    """
    
    def __init__(self, config_path: str = '.env'):
        """
        Initialize the SaltService with configuration.
        
        Args:
            config_path (str): Path to environment configuration file
        """
        self.config = read_env_file(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize repository with configuration
        sqlite_path = self.config.get('sqlite_db_path', 'db/kasa.db')
        redis_host = self.config.get('host', 'localhost')
        redis_port = int(self.config.get('port', 6379))
        redis_db = int(self.config.get('db', 0))
        
        self.repository = SaltRepository(
            sqlite_path=sqlite_path,
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db
        )
    
    def create_salt(self, method: str = "sha256", salt_value: Optional[str] = None) -> int:
        """
        Create a new salt with specified method and optional custom salt value.
        
        Args:
            method (str): Hashing method for the salt (sha256, sha512, md5, argon2)
            salt_value (Optional[str]): Custom salt value, if None generates random salt
            
        Returns:
            int: ID of the created salt record
            
        Raises:
            ValueError: If method is not supported
            Exception: If salt creation fails
        """
        try:
            # Validate method
            salt_instance = Salt(method=method, salt=salt_value)
            
            # Convert to model and save
            salt_model = salt_instance.toDTO()
            salt_id = self.repository.add(salt_model)
            
            self.logger.info(f"Salt created successfully with ID: {salt_id}, method: {method}")
            # print(ModelSalt(id=salt_id, method=method, salt=salt_model.salt))
            return salt_id

        except ValueError as e:
            self.logger.error(f"Invalid salt method: {method}. Error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create salt: {str(e)}")
            raise Exception(f"Salt creation failed: {str(e)}")
    
    def get_salt(self, salt_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve salt by ID.
        
        Args:
            salt_id (int): ID of the salt to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Salt data or None if not found
        """
        try:
            salt_model = self.repository.get(salt_id)
            if salt_model:
                return salt_model.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve salt {salt_id}: {str(e)}")
            raise Exception(f"Salt retrieval failed: {str(e)}")
    
    def _apply_salt_to_key(self, salt_id: int, secret_key: str) -> str:
        """
        Apply salt to a secret key using the stored salt configuration.
        
        Args:
            salt_id (int): ID of the salt to use
            secret_key (str): The secret key to salt
            
        Returns:
            str: Salted and hashed key
            
        Raises:
            ValueError: If salt not found or invalid
            Exception: If salting process fails
        """
        try:
            # Retrieve salt configuration
            salt_model = self.repository.get(salt_id)
            if not salt_model:
                raise ValueError(f"Salt with ID {salt_id} not found")
            
            # Create salt instance and apply to key
            salt_instance = Salt(method=salt_model.method, salt=salt_model.salt)
            salted_key = salt_instance.apply_salt(secret_key)
            
            self.logger.debug(f"Salt applied successfully to key using salt ID: {salt_id}")
            return salted_key
            
        except ValueError as e:
            self.logger.error(f"Salt application failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during salt application: {str(e)}")
            raise Exception(f"Salt application failed: {str(e)}")
    
    def delete_all_salts(self) -> bool:
        """
        Delete all salts from the repository.
        
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            self.repository.delete_all()
            self.logger.info("All salts deleted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete all salts: {str(e)}")
            return False
    
    def delete_salt(self, salt_id: int) -> bool:
        """
        Delete a salt by ID.
        
        Args:
            salt_id (int): ID of the salt to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # Check if salt exists
            existing_salt = self.repository.get(salt_id)
            if not existing_salt:
                self.logger.warning(f"Attempted to delete non-existent salt: {salt_id}")
                return False
            
            self.repository.delete(salt_id)
            self.logger.info(f"Salt {salt_id} deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete salt {salt_id}: {str(e)}")
            return False
    
    def list_all_salts(self) -> List[Dict[str, Any]]:
        """
        Retrieve all salts.
        
        Returns:
            List[Dict[str, Any]]: List of all salt records
        """
        try:
            salt_models = self.repository.get_all()
            return [salt.to_dict() for salt in salt_models]
        except Exception as e:
            self.logger.error(f"Failed to retrieve all salts: {str(e)}")
            raise Exception(f"Salt list retrieval failed: {str(e)}")
    
    def get_supported_methods(self) -> List[str]:
        """
        Get list of supported hashing methods.
        
        Returns:
            List[str]: List of supported methods
        """
        try:
            salt_instance = Salt()
            return salt_instance.get_methods()
        except Exception as e:
            self.logger.error(f"Failed to retrieve supported methods: {str(e)}")
            return ["sha256", "sha512", "md5"]  # fallback
    
    
    
    def generate_salt_for_key(self, secret_key: str, method: str = "sha256") -> Dict[str, Any]:
        """
        Generate a new salt and immediately apply it to a secret key.
        This is a convenience method for one-time salt operations.
        
        Args:
            secret_key (str): The secret key to salt
            method (str): Hashing method to use
            
        Returns:
            Dict[str, Any]: Contains salt_id, salted_key, and salt_info
        """
        try:
            # Create salt
            salt_id = self.create_salt(method=method)
            
            # Apply salt to key
            salted_key = self._apply_salt_to_key(salt_id, secret_key)
            
            # Get salt info
            salt_info = self.get_salt(salt_id)
            
            return {
                "salt_id": salt_id,
                "salted_key": salted_key,
                "salt_info": salt_info,
                "method": method
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate and apply salt: {str(e)}")
            raise Exception(f"Salt generation and application failed: {str(e)}")
    

# Example usage and testing
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    service = SaltService()
    
    try:
        # Test salt creation
        salt_id = service.create_salt(method="sha256")
        print(f"Created salt with ID: {salt_id}")
        
        # Test salt application
        secret_key = "my_secret_password"
        salted_key = service._apply_salt_to_key(salt_id, secret_key)
        print(f"Salted key: {salted_key}")
        
        # Test salt retrieval
        salt_info = service.get_salt(salt_id)
        print(f"Salt info: {salt_info}")
        
        # Test supported methods
        methods = service.get_supported_methods()
        print(f"Supported methods: {methods}")
        
    except Exception as e:
        print(f"Error: {e}")
