from typing import Optional, List, Dict, Any
from src.cyrpto.encryptor import Encryptor
from src.cyrpto.decrptor import Decryptor
from src.model.model_cipher import ModelCipher
from src.repository.cipherRepository import CipherRepository
from src.utils.enviroment_variable import read_env_file
from src.services.saltService import SaltService
import logging


class CipherService:
    """
    Service layer for cipher management operations.
    Handles business logic for encryption, decryption, and cipher persistence.
    """
    
    def __init__(self, config_path: str = '.env'):
        """
        Initialize the CipherService with configuration.
        
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
        
        self.repository = CipherRepository(
            sqlite_path=sqlite_path,
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db
        )
        
        # Initialize salt service for salt-based cipher operations
        self.salt_service = SaltService(config_path=config_path)
    
    def create_cipher(self, name: str, plaintext: str, method: str, key: str) -> int:
        """
        Create a new cipher by encrypting plaintext with specified method and key.
        
        Args:
            name (str): Name/identifier for the cipher
            plaintext (str): The data to encrypt
            method (str): Encryption method (aes128, aes256, chacha20)
            key (str): Encryption key
            
        Returns:
            int: ID of the created cipher record
            
        Raises:
            ValueError: If method is not supported
            Exception: If cipher creation fails
        """
        try:
            # Validate method and encrypt data
            encryptor = Encryptor(method_name=method, key=key)
            encrypted_data = encryptor.encrypt(plaintext)
            
            # Create model and save
            cipher_model = ModelCipher(
                name=name,
                encrypted_cipher=encrypted_data,
                method=method
            )
            cipher_id = self.repository.add(cipher_model)
            
            self.logger.info(f"Cipher created successfully with ID: {cipher_id}, method: {method}, name: {name}")
            return cipher_id

        except ValueError as e:
            self.logger.error(f"Invalid encryption method: {method}. Error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create cipher: {str(e)}")
            raise Exception(f"Cipher creation failed: {str(e)}")
    
    def get_cipher(self, cipher_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve cipher by ID.
        
        Args:
            cipher_id (int): ID of the cipher to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Cipher data or None if not found
        """
        try:
            cipher_model = self.repository.get(cipher_id)
            if cipher_model:
                return cipher_model.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve cipher {cipher_id}: {str(e)}")
            raise Exception(f"Cipher retrieval failed: {str(e)}")
    
    def decrypt_cipher(self, cipher_id: int, key: str) -> str:
        """
        Decrypt a cipher using the provided key.
        
        Args:
            cipher_id (int): ID of the cipher to decrypt
            key (str): Decryption key
            
        Returns:
            str: Decrypted plaintext
            
        Raises:
            ValueError: If cipher not found or invalid
            Exception: If decryption process fails
        """
        try:
            # Retrieve cipher
            cipher_model = self.repository.get(cipher_id)
            if not cipher_model:
                raise ValueError(f"Cipher with ID {cipher_id} not found")
            
            # Create decryptor and decrypt
            decryptor = Decryptor(method_name=cipher_model.method, key=key)
            plaintext = decryptor.decrypt(cipher_model.encrypted_cipher)
            
            self.logger.debug(f"Cipher decrypted successfully for ID: {cipher_id}")
            return plaintext
            
        except ValueError as e:
            self.logger.error(f"Cipher decryption failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during cipher decryption: {str(e)}")
            raise Exception(f"Cipher decryption failed: {str(e)}")
    
    def update_cipher(self, cipher_id: int, name: Optional[str] = None, 
                     plaintext: Optional[str] = None, method: Optional[str] = None, 
                     key: Optional[str] = None) -> bool:
        """
        Update an existing cipher.
        
        Args:
            cipher_id (int): ID of the cipher to update
            name (Optional[str]): New name for the cipher
            plaintext (Optional[str]): New plaintext to encrypt
            method (Optional[str]): New encryption method
            key (Optional[str]): New encryption key
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Check if cipher exists
            existing_cipher = self.repository.get(cipher_id)
            if not existing_cipher:
                self.logger.warning(f"Attempted to update non-existent cipher: {cipher_id}")
                return False
            
            # Prepare updated model
            updated_cipher = ModelCipher(
                id=cipher_id,
                name=name if name is not None else existing_cipher.name,
                encrypted_cipher=existing_cipher.encrypted_cipher,
                method=method if method is not None else existing_cipher.method
            )
            
            # If new plaintext or method provided, re-encrypt
            if plaintext is not None or method is not None or key is not None:
                if not key:
                    raise ValueError("Key is required when updating plaintext or method")
                
                new_plaintext = plaintext if plaintext is not None else self.decrypt_cipher(cipher_id, key)
                new_method = method if method is not None else existing_cipher.method
                
                encryptor = Encryptor(method_name=new_method, key=key)
                updated_cipher.encrypted_cipher = encryptor.encrypt(new_plaintext)
                updated_cipher.method = new_method
            
            self.repository.update(cipher_id, updated_cipher)
            self.logger.info(f"Cipher {cipher_id} updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update cipher {cipher_id}: {str(e)}")
            return False
    
    def delete_cipher(self, cipher_id: int) -> bool:
        """
        Delete a cipher by ID.
        
        Args:
            cipher_id (int): ID of the cipher to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # Check if cipher exists
            existing_cipher = self.repository.get(cipher_id)
            if not existing_cipher:
                self.logger.warning(f"Attempted to delete non-existent cipher: {cipher_id}")
                return False
            
            self.repository.delete(cipher_id)
            self.logger.info(f"Cipher {cipher_id} deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete cipher {cipher_id}: {str(e)}")
            return False
    
    def list_all_ciphers(self) -> List[Dict[str, Any]]:
        """
        Retrieve all ciphers.
        
        Returns:
            List[Dict[str, Any]]: List of all cipher records
        """
        try:
            cipher_models = self.repository.get_all()
            return [cipher.to_dict() for cipher in cipher_models]
        except Exception as e:
            self.logger.error(f"Failed to retrieve all ciphers: {str(e)}")
            raise Exception(f"Cipher list retrieval failed: {str(e)}")
    
    def get_supported_methods(self) -> List[str]:
        """
        Get list of supported encryption methods.
        
        Returns:
            List[str]: List of supported methods
        """
        try:
            # Return available encryption methods
            return ["aes128", "aes256", "chacha20"]
        except Exception as e:
            self.logger.error(f"Failed to retrieve supported methods: {str(e)}")
            return ["aes128", "aes256", "chacha20"]  # fallback
    
    def search_ciphers_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """
        Search ciphers by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for in cipher names
            
        Returns:
            List[Dict[str, Any]]: List of matching cipher records
        """
        try:
            all_ciphers = self.list_all_ciphers()
            matching_ciphers = [
                cipher for cipher in all_ciphers 
                if name_pattern.lower() in cipher['name'].lower()
            ]
            return matching_ciphers
        except Exception as e:
            self.logger.error(f"Failed to search ciphers: {str(e)}")
            raise Exception(f"Cipher search failed: {str(e)}")
    
    def encrypt_and_store(self, name: str, plaintext: str, method: str = "aes256", key: str = None) -> Dict[str, Any]:
        """
        Encrypt data and store it as a cipher. This is a convenience method.
        
        Args:
            name (str): Name for the cipher
            plaintext (str): Data to encrypt
            method (str): Encryption method to use
            key (str): Encryption key
            
        Returns:
            Dict[str, Any]: Contains cipher_id, method, and cipher_info
        """
        try:
            if not key:
                raise ValueError("Encryption key is required")
            
            # Create cipher
            cipher_id = self.create_cipher(name=name, plaintext=plaintext, method=method, key=key)
            
            # Get cipher info
            cipher_info = self.get_cipher(cipher_id)
            
            return {
                "cipher_id": cipher_id,
                "method": method,
                "cipher_info": cipher_info,
                "name": name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt and store: {str(e)}")
            raise Exception(f"Encrypt and store operation failed: {str(e)}")
    
    def create_cipher_with_first_salt_key(self, name: str, plaintext: str, method: str = "aes256") -> Dict[str, Any]:
        """
        Create a new cipher using the first salt from database as the cipher key.
        Uses the salt ID = 1 as the encryption key.
        
        Args:
            name (str): Name/identifier for the cipher
            plaintext (str): The data to encrypt
            method (str): Encryption method (aes128, aes256, chacha20)
            
        Returns:
            Dict[str, Any]: Contains cipher_id, salt_id_used, cipher_info, and salt_info
            
        Raises:
            ValueError: If first salt not found or method is not supported
            Exception: If cipher creation fails
        """
        try:
            # Get the first salt (ID = 1) from database
            first_salt_id = 1
            salt_info = self.salt_service.get_salt(first_salt_id)
            
            if not salt_info:
                raise ValueError(f"First salt with ID {first_salt_id} not found in database. Please create a salt first.")
            
            # Use the salt ID as the cipher key
            cipher_key = str(first_salt_id)
            
            self.logger.info(f"Using first salt ID ({first_salt_id}) as cipher key")
            
            # Create cipher with the salt ID as key
            cipher_id = self.create_cipher(
                name=name, 
                plaintext=plaintext, 
                method=method, 
                key=cipher_key
            )
            
            # Get cipher info
            cipher_info = self.get_cipher(cipher_id)
            
            result = {
                "cipher_id": cipher_id,
                "salt_id_used": first_salt_id,
                "cipher_key_used": cipher_key,
                "cipher_method": method,
                "cipher_info": cipher_info,
                "salt_info": salt_info,
                "name": name
            }
            
            self.logger.info(f"Cipher created with first salt key. Cipher ID: {cipher_id}, Salt ID used: {first_salt_id}")
            return result
            
        except ValueError as e:
            self.logger.error(f"Failed to create cipher with first salt key: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create cipher with first salt key: {str(e)}")
            raise Exception(f"Cipher creation with first salt key failed: {str(e)}")
    
    def decrypt_cipher_with_first_salt_key(self, cipher_id: int) -> str:
        """
        Decrypt a cipher that was created using the first salt ID as the key.
        
        Args:
            cipher_id (int): ID of the cipher to decrypt
            
        Returns:
            str: Decrypted plaintext
            
        Raises:
            ValueError: If cipher not found or first salt not available
            Exception: If decryption process fails
        """
        try:
            # Use first salt ID as the decryption key
            first_salt_id = 1
            cipher_key = str(first_salt_id)
            
            # Verify first salt still exists
            salt_info = self.salt_service.get_salt(first_salt_id)
            if not salt_info:
                raise ValueError(f"First salt with ID {first_salt_id} not found. Cannot decrypt cipher.")
            
            # Decrypt using the first salt ID as key
            plaintext = self.decrypt_cipher(cipher_id, cipher_key)
            
            self.logger.debug(f"Cipher decrypted using first salt key. Cipher ID: {cipher_id}, Salt ID used: {first_salt_id}")
            return plaintext
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt cipher with first salt key: {str(e)}")
            raise Exception(f"Cipher decryption with first salt key failed: {str(e)}")
    
    def decrypt_cipher_by_name_with_first_salt_key(self, cipher_name: str) -> Dict[str, Any]:
        """
        Search for a cipher by name and decrypt it using the first salt key.
        
        Args:
            cipher_name (str): Name or partial name of the cipher to search and decrypt
            
        Returns:
            Dict[str, Any]: Contains decrypted_text, cipher_info, and search_results
            
        Raises:
            ValueError: If no cipher found or multiple ciphers found
            Exception: If decryption process fails
        """
        try:
            # Search for ciphers with matching name
            matching_ciphers = self.search_ciphers_by_name(cipher_name)
            
            if not matching_ciphers:
                raise ValueError(f"No ciphers found with name containing '{cipher_name}'")
            
            if len(matching_ciphers) > 1:
                # Multiple matches found - return information for user to choose
                cipher_list = []
                for cipher in matching_ciphers:
                    cipher_list.append({
                        "id": cipher["id"],
                        "name": cipher["name"], 
                        "method": cipher["method"]
                    })
                
                raise ValueError(f"Multiple ciphers found ({len(matching_ciphers)}). Please be more specific. Found: {cipher_list}")
            
            # Single match found - decrypt it
            cipher = matching_ciphers[0]
            cipher_id = cipher["id"]
            
            if cipher["name"] != cipher_name:
                raise ValueError(f"Cipher name '{cipher_name}' does not match any existing cipher. Proceeding with decryption.")

            
            self.logger.info(f"Found single cipher match: '{cipher['name']}' (ID: {cipher_id})")
            
            # Decrypt using first salt key
            decrypted_text = self.decrypt_cipher_with_first_salt_key(cipher_id)
            
            result = {
                "decrypted_text": decrypted_text,
                "cipher_info": cipher,
                "cipher_id": cipher_id,
                "cipher_name": cipher["name"],
                "method": cipher["method"],
                "search_term": cipher_name,
                "matches_found": 1
            }
            
            self.logger.info(f"Successfully decrypted cipher '{cipher['name']}' using first salt key")
            return result
            
        except ValueError as e:
            self.logger.error(f"Cipher search/decrypt by name failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to decrypt cipher by name with first salt key: {str(e)}")
            raise Exception(f"Cipher decrypt by name failed: {str(e)}")
    
    def get_cipher_suggestions_by_name(self, cipher_name: str) -> List[Dict[str, Any]]:
        """
        Get cipher suggestions by name for cases with multiple matches.
        This is a helper method for decrypt_cipher_by_name_with_first_salt_key.
        
        Args:
            cipher_name (str): Name or partial name to search for
            
        Returns:
            List[Dict[str, Any]]: List of cipher suggestions with essential info
        """
        try:
            matching_ciphers = self.search_ciphers_by_name(cipher_name)
            
            suggestions = []
            for cipher in matching_ciphers:
                suggestions.append({
                    "id": cipher["id"],
                    "name": cipher["name"],
                    "method": cipher["method"],
                    "encrypted_preview": cipher.get("encrypted_cipher", "")[:20] + "..."
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get cipher suggestions: {str(e)}")
            return []


# Example usage and testing
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    service = CipherService()
    
    try:
        # Test cipher creation
        test_key = "my_secret_key_123"
        test_plaintext = "This is my secret message"
        cipher_id = service.create_cipher(
            name="test_cipher", 
            plaintext=test_plaintext, 
            method="aes256", 
            key=test_key
        )
        print(f"Created cipher with ID: {cipher_id}")
        
        # Test cipher retrieval
        cipher_info = service.get_cipher(cipher_id)
        print(f"Cipher info: {cipher_info}")
        
        # Test decryption
        decrypted_text = service.decrypt_cipher(cipher_id, test_key)
        print(f"Decrypted text: {decrypted_text}")
        
        # Test supported methods
        methods = service.get_supported_methods()
        print(f"Supported methods: {methods}")
        
        # Test encrypt and store convenience method
        result = service.encrypt_and_store(
            name="convenience_test",
            plaintext="Another secret message",
            method="aes128",
            key=test_key
        )
        print(f"Encrypt and store result: {result}")
        
        # Test cipher creation with first salt key
        # First, ensure we have a salt with ID 1
        try:
            first_salt_result = service.create_cipher_with_first_salt_key(
                name="first_salt_test",
                plaintext="This cipher uses first salt ID as key",
                method="aes256"
            )
            print(f"First salt cipher result: {first_salt_result}")
            
            # Test decryption with first salt key
            decrypted_first_salt = service.decrypt_cipher_with_first_salt_key(
                cipher_id=first_salt_result["cipher_id"]
            )
            print(f"Decrypted first salt text: {decrypted_first_salt}")
            
            # Test decrypt by name with first salt key
            try:
                decrypt_by_name_result = service.decrypt_cipher_by_name_with_first_salt_key("first_salt_test")
                print(f"Decrypt by name result: {decrypt_by_name_result['decrypted_text']}")
                print(f"Found cipher: {decrypt_by_name_result['cipher_name']} (ID: {decrypt_by_name_result['cipher_id']})")
            except ValueError as name_error:
                print(f"Decrypt by name error: {name_error}")
            
        except ValueError as ve:
            print(f"First salt method error (this is expected if no salt with ID 1 exists): {ve}")
            # Try creating a salt first
            try:
                salt_id = service.salt_service.create_salt(method="sha256")
                print(f"Created salt with ID: {salt_id}")
                if salt_id == 1:
                    print("Retrying first salt cipher creation...")
                    first_salt_result = service.create_cipher_with_first_salt_key(
                        name="first_salt_test_retry",
                        plaintext="This cipher uses first salt ID as key - retry",
                        method="aes256"
                    )
                    print(f"First salt cipher result (retry): {first_salt_result}")
            except Exception as se:
                print(f"Salt creation error: {se}")
        
    except Exception as e:
        print(f"Error: {e}")