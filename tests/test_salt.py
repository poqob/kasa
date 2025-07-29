import pytest
from src.model.model_salt import ModelSalt
from src.repository.sqlite import SqliteRepository
from src.services.saltService import SaltService
from src.utils.enviroment_variable import read_env_file
from src.cyrpto.salt import Salt
from src.services.cipherService import CipherService


class TestSaltService:
    """Test class for Salt Service functionality."""
    
    def test_get_supported_methods(self, salt_service):
        """Test that supported salt methods are returned."""
        methods = salt_service.get_supported_methods()
        assert isinstance(methods, list)
        assert len(methods) > 0
        assert "sha256" in methods
        assert "sha512" in methods
        assert "md5" in methods
        assert "argon2" in methods
    
    def test_create_salt_default_method(self, salt_service):
        """Test creating a salt with default method."""
        salt_id = salt_service.create_salt()
        assert isinstance(salt_id, int)
        assert salt_id > 0
        
        # Verify the salt was created
        salt = salt_service.get_salt(salt_id)
        assert salt is not None
        assert salt['id'] == salt_id
        assert salt['method'] == "sha256"  # default method
        assert len(salt['salt']) > 0
    
    def test_create_salt_with_method(self, salt_service):
        """Test creating a salt with specific method."""
        methods_to_test = ["sha256", "sha512", "md5"]
        
        for method in methods_to_test:
            salt_id = salt_service.create_salt(method=method)
            assert isinstance(salt_id, int)
            assert salt_id > 0
            
            # Verify the salt was created with correct method
            salt = salt_service.get_salt(salt_id)
            assert salt is not None
            assert salt['method'] == method
            assert len(salt['salt']) > 0
    
    def test_create_salt_with_custom_value(self, salt_service):
        """Test creating a salt with custom salt value."""
        custom_salt = "my_custom_salt_value"
        salt_id = salt_service.create_salt(method="sha256", salt_value=custom_salt)
        
        assert isinstance(salt_id, int)
        assert salt_id > 0
        
        # Verify the salt was created
        salt = salt_service.get_salt(salt_id)
        assert salt is not None
        assert custom_salt in salt['salt']  # Custom value should be part of the salt
    
    def test_get_salt_existing(self, salt_service):
        """Test getting an existing salt."""
        # Create a salt first
        salt_id = salt_service.create_salt(method="sha256")
        
        # Get the salt
        salt = salt_service.get_salt(salt_id)
        assert salt is not None
        assert salt['id'] == salt_id
        assert salt['method'] == "sha256"
        assert len(salt['salt']) > 0
    
    def test_get_salt_non_existing(self, salt_service):
        """Test getting a non-existing salt."""
        salt = salt_service.get_salt(99999)  # Assuming this ID doesn't exist
        assert salt is None
    
    def test_list_all_salts(self, salt_service):
        """Test listing all salts."""
        # Create a few salts
        salt_ids = []
        for method in ["sha256", "sha512"]:
            salt_id = salt_service.create_salt(method=method)
            salt_ids.append(salt_id)
        
        # List all salts
        salts = salt_service.list_all_salts()
        assert isinstance(salts, list)
        assert len(salts) >= len(salt_ids)
        
        # Check that our created salts are in the list
        salt_ids_in_list = [salt['id'] for salt in salts]
        for salt_id in salt_ids:
            assert salt_id in salt_ids_in_list
    
    def test_delete_salt(self, salt_service):
        """Test deleting a salt."""
        # Create a salt
        salt_id = salt_service.create_salt(method="sha256")
        
        # Verify it exists
        salt = salt_service.get_salt(salt_id)
        assert salt is not None
        
        # Delete it
        result = salt_service.delete_salt(salt_id)
        assert result is True
        
        # Verify it's gone
        salt = salt_service.get_salt(salt_id)
        assert salt is None
    
    def test_delete_non_existing_salt(self, salt_service):
        """Test deleting a non-existing salt."""
        result = salt_service.delete_salt(99999)  # Assuming this ID doesn't exist
        assert result is False
    
    def test_generate_salt_for_key(self, salt_service):
        """Test generating salt for a specific key."""
        secret_key = "test_secret_key"
        method = "sha256"
        
        result = salt_service.generate_salt_for_key(secret_key, method)
        
        assert isinstance(result, dict)
        assert 'salt_id' in result
        assert 'method' in result
        assert 'salted_key' in result
        assert result['method'] == method
        assert isinstance(result['salt_id'], int)
        assert len(result['salted_key']) > 0
        
        # Verify the salt was actually created
        salt = salt_service.get_salt(result['salt_id'])
        assert salt is not None
        assert salt['method'] == method


class TestSaltModel:
    """Test class for Salt model functionality."""
    
    def test_salt_creation_sha256(self):
        """Test creating a salt with SHA256."""
        salt = Salt(method="sha256")
        secret_key = "test_key"
        salted_key = salt.apply_salt(secret_key=secret_key)
        
        assert len(salted_key) > len(secret_key)
        assert secret_key != salted_key
        assert isinstance(salted_key, str)
    
    def test_salt_creation_sha512(self):
        """Test creating a salt with SHA512."""
        salt = Salt(method="sha512")
        secret_key = "test_key"
        salted_key = salt.apply_salt(secret_key=secret_key)
        
        assert len(salted_key) > len(secret_key)
        assert secret_key != salted_key
        assert isinstance(salted_key, str)
    
    def test_salt_creation_md5(self):
        """Test creating a salt with MD5."""
        salt = Salt(method="md5")
        secret_key = "test_key"
        salted_key = salt.apply_salt(secret_key=secret_key)
        
        assert len(salted_key) > len(secret_key)
        assert secret_key != salted_key
        assert isinstance(salted_key, str)
    
    def test_salt_consistency(self):
        """Test that the same salt produces the same result."""
        salt1 = Salt(method="sha256")
        salt2 = Salt(method="sha256")
        
        # Different salt instances should produce different results
        secret_key = "test_key"
        result1 = salt1.apply_salt(secret_key=secret_key)
        result2 = salt2.apply_salt(secret_key=secret_key)
        
        # Results should be different because salts are different
        assert result1 != result2
    
    def test_model_salt_creation(self):
        """Test ModelSalt creation."""
        method = "sha256"
        salt_value = "test_salt_value"
        
        model_salt = ModelSalt(method=method, salt=salt_value)
        
        assert model_salt.method == method
        assert model_salt.salt == salt_value
        
        # Test to_dict method
        salt_dict = model_salt.to_dict()
        assert isinstance(salt_dict, dict)
        assert salt_dict['method'] == method
        assert salt_dict['salt'] == salt_value


class TestSaltRepository:
    """Test class for Salt repository functionality."""
    
    def test_salt_repository_operations(self):
        """Test basic salt repository operations."""
        sql_path = read_env_file().get('sqlite_db_path', 'db/kasa.db')
        repo = SqliteRepository(db_url=f'sqlite:///{sql_path}', model_name='salt')
        
        # Create a test salt
        test_salt = ModelSalt(method="sha256", salt="test_salt_value")
        
        # Add to repository
        repo.add(test_salt)
        
        # Verify we can retrieve it
        if hasattr(test_salt, 'id') and test_salt.id:
            retrieved_salt = repo.get(test_salt.id)
            assert retrieved_salt is not None
            assert retrieved_salt.method == test_salt.method
            assert retrieved_salt.salt == test_salt.salt
        
        # Test get_all
        all_salts = repo.get_all()
        assert isinstance(all_salts, list)
        assert len(all_salts) > 0
