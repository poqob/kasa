
import pytest
from src.services.cipherService import CipherService


class TestCipherService:
    """Test class for Cipher Service functionality."""
    
    def test_get_supported_methods(self, cipher_service):
        """Test that supported cipher methods are returned."""
        methods = cipher_service.get_supported_methods()
        assert isinstance(methods, list)
        assert len(methods) > 0
        assert "aes128" in methods
        assert "aes256" in methods
        assert "chacha20" in methods
    
    def test_first_salt_key_cipher_creation(self, cipher_service, setup_first_salt, cleanup_test_ciphers, test_data):
        """Test creating ciphers with first salt key."""
        created_ciphers = []
        
        for test_case in test_data:
            result = cipher_service.create_cipher_with_first_salt_key(
                name=test_case["name"],
                plaintext=test_case["plaintext"],
                method=test_case["method"]
            )
            
            # Track for cleanup
            cleanup_test_ciphers(result['cipher_id'])
            created_ciphers.append(result)
            
            # Assertions
            assert isinstance(result, dict)
            assert 'cipher_id' in result
            assert 'name' in result
            assert 'cipher_method' in result
            assert 'salt_id_used' in result
            assert 'cipher_key_used' in result
            
            assert result['name'] == test_case["name"]
            assert result['cipher_method'] == test_case["method"]
            assert isinstance(result['cipher_id'], int)
            assert result['cipher_id'] > 0
            assert result['salt_id_used'] == 1  # Should use first salt
    
    def test_first_salt_key_cipher_decryption(self, cipher_service, setup_first_salt, cleanup_test_ciphers, test_data):
        """Test decrypting ciphers with first salt key."""
        # First create ciphers
        created_ciphers = []
        
        for test_case in test_data:
            result = cipher_service.create_cipher_with_first_salt_key(
                name=test_case["name"],
                plaintext=test_case["plaintext"],
                method=test_case["method"]
            )
            cleanup_test_ciphers(result['cipher_id'])
            created_ciphers.append((result, test_case))
        
        # Now test decryption
        for result, original_test_case in created_ciphers:
            decrypted_text = cipher_service.decrypt_cipher_with_first_salt_key(
                cipher_id=result["cipher_id"]
            )
            
            assert decrypted_text == original_test_case["plaintext"]
            assert isinstance(decrypted_text, str)
    
    def test_cipher_by_name_operations(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test cipher operations by name."""
        # Create a test cipher
        test_name = "test_cipher_by_name"
        test_plaintext = "This is a test message for name-based operations"
        test_method = "aes256"
        
        result = cipher_service.create_cipher_with_first_salt_key(
            name=test_name,
            plaintext=test_plaintext,
            method=test_method
        )
        cleanup_test_ciphers(result['cipher_id'])
        
        # Test decrypt by name
        decrypt_result = cipher_service.decrypt_cipher_by_name_with_first_salt_key(test_name)
        
        assert isinstance(decrypt_result, dict)
        assert 'decrypted_text' in decrypt_result
        assert 'cipher_name' in decrypt_result
        assert 'cipher_id' in decrypt_result
        assert 'method' in decrypt_result
        assert 'search_term' in decrypt_result
        
        assert decrypt_result['decrypted_text'] == test_plaintext
        assert decrypt_result['cipher_name'] == test_name
        assert decrypt_result['cipher_id'] == result['cipher_id']
        assert decrypt_result['method'] == test_method
        assert decrypt_result['search_term'] == test_name
    
    def test_search_ciphers_by_name(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test searching ciphers by name pattern."""
        # Create test ciphers with similar names
        test_prefix = "search_test"
        test_ciphers = [
            f"{test_prefix}_cipher_1",
            f"{test_prefix}_cipher_2", 
            f"{test_prefix}_different"
        ]
        
        created_ids = []
        for name in test_ciphers:
            result = cipher_service.create_cipher_with_first_salt_key(
                name=name,
                plaintext=f"Content for {name}",
                method="aes256"
            )
            cleanup_test_ciphers(result['cipher_id'])
            created_ids.append(result['cipher_id'])
        
        # Search by pattern
        search_results = cipher_service.search_ciphers_by_name(test_prefix)
        
        assert isinstance(search_results, list)
        assert len(search_results) >= len(test_ciphers)
        
        # Check that our created ciphers are in results
        result_names = [cipher['name'] for cipher in search_results]
        for test_name in test_ciphers:
            assert test_name in result_names
    
    def test_list_all_ciphers(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test listing all ciphers."""
        # Create a test cipher
        result = cipher_service.create_cipher_with_first_salt_key(
            name="test_list_cipher",
            plaintext="Test content for listing",
            method="aes128"
        )
        cleanup_test_ciphers(result['cipher_id'])
        
        # List all ciphers
        all_ciphers = cipher_service.list_all_ciphers()
        
        assert isinstance(all_ciphers, list)
        assert len(all_ciphers) > 0
        
        # Check that our cipher is in the list
        cipher_ids = [cipher['id'] for cipher in all_ciphers]
        assert result['cipher_id'] in cipher_ids
    
    def test_get_cipher_by_id(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test getting cipher by ID."""
        # Create a test cipher
        result = cipher_service.create_cipher_with_first_salt_key(
            name="test_get_cipher",
            plaintext="Test content for getting",
            method="chacha20"
        )
        cleanup_test_ciphers(result['cipher_id'])
        
        # Get cipher by ID
        cipher = cipher_service.get_cipher(result['cipher_id'])
        
        assert cipher is not None
        assert isinstance(cipher, dict)
        assert cipher['id'] == result['cipher_id']
        assert cipher['name'] == "test_get_cipher"
        assert cipher['method'] == "chacha20"
        assert 'encrypted_cipher' in cipher
    
    def test_delete_cipher(self, cipher_service, setup_first_salt):
        """Test deleting a cipher."""
        # Create a test cipher
        result = cipher_service.create_cipher_with_first_salt_key(
            name="test_delete_cipher",
            plaintext="Test content for deletion",
            method="aes256"
        )
        cipher_id = result['cipher_id']
        
        # Verify it exists
        cipher = cipher_service.get_cipher(cipher_id)
        assert cipher is not None
        
        # Delete it
        delete_result = cipher_service.delete_cipher(cipher_id)
        assert delete_result is True
        
        # Verify it's gone
        cipher = cipher_service.get_cipher(cipher_id)
        assert cipher is None
    
    def test_error_handling_non_existent_cipher(self, cipher_service, setup_first_salt):
        """Test error handling for non-existent ciphers."""
        with pytest.raises(Exception):
            cipher_service.decrypt_cipher_with_first_salt_key(cipher_id=99999)
    
    def test_error_handling_multiple_matches(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test error handling for multiple name matches."""
        # Create multiple ciphers with similar names
        base_name = "duplicate_test"
        for i in range(2):
            result = cipher_service.create_cipher_with_first_salt_key(
                name=f"{base_name}_{i}",
                plaintext=f"Content {i}",
                method="aes256"
            )
            cleanup_test_ciphers(result['cipher_id'])
        
        # Try to decrypt by partial name (should match multiple)
        with pytest.raises(ValueError, match="Multiple ciphers found"):
            cipher_service.decrypt_cipher_by_name_with_first_salt_key(base_name)


class TestCipherComprehensive:
    """Comprehensive tests for cipher functionality with edge cases."""
    
    def test_comprehensive_cipher_operations(self, cipher_service, setup_first_salt, cleanup_test_ciphers, comprehensive_test_data):
        """Test cipher operations with various data types and edge cases."""
        for test_case in comprehensive_test_data:
            # Create cipher
            create_result = cipher_service.create_cipher_with_first_salt_key(
                name=test_case["name"],
                plaintext=test_case["plaintext"],
                method=test_case["method"]
            )
            cleanup_test_ciphers(create_result['cipher_id'])
            
            # Verify creation
            assert isinstance(create_result, dict)
            assert create_result['name'] == test_case["name"]
            assert create_result['cipher_method'] == test_case["method"]
            
            # Test decryption
            decrypted = cipher_service.decrypt_cipher_with_first_salt_key(
                cipher_id=create_result["cipher_id"]
            )
            
            # Verify decryption matches original
            assert decrypted == test_case["plaintext"]
            assert isinstance(decrypted, str)
    
    def test_empty_string_encryption(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test encryption of empty string."""
        result = cipher_service.create_cipher_with_first_salt_key(
            name="empty_test",
            plaintext="",
            method="aes256"
        )
        cleanup_test_ciphers(result['cipher_id'])
        
        decrypted = cipher_service.decrypt_cipher_with_first_salt_key(result['cipher_id'])
        assert decrypted == ""
    
    def test_unicode_encryption(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test encryption of unicode characters."""
        unicode_text = "🔐 Unicode test: áéíóú ñç 中文 русский ⚡"
        
        result = cipher_service.create_cipher_with_first_salt_key(
            name="unicode_test",
            plaintext=unicode_text,
            method="aes256"
        )
        cleanup_test_ciphers(result['cipher_id'])
        
        decrypted = cipher_service.decrypt_cipher_with_first_salt_key(result['cipher_id'])
        assert decrypted == unicode_text
    
    def test_large_text_encryption(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test encryption of large text."""
        large_text = "Large text content. " * 1000  # ~20KB of text
        
        result = cipher_service.create_cipher_with_first_salt_key(
            name="large_test",
            plaintext=large_text,
            method="aes256"
        )
        cleanup_test_ciphers(result['cipher_id'])
        
        decrypted = cipher_service.decrypt_cipher_with_first_salt_key(result['cipher_id'])
        assert decrypted == large_text
        assert len(decrypted) == len(large_text)
    
    def test_all_encryption_methods(self, cipher_service, setup_first_salt, cleanup_test_ciphers):
        """Test all supported encryption methods."""
        methods = cipher_service.get_supported_methods()
        test_plaintext = "Test message for all methods"
        
        for method in methods:
            result = cipher_service.create_cipher_with_first_salt_key(
                name=f"method_test_{method}",
                plaintext=test_plaintext,
                method=method
            )
            cleanup_test_ciphers(result['cipher_id'])
            
            # Verify the correct method was used
            assert result['cipher_method'] == method
            
            # Test decryption
            decrypted = cipher_service.decrypt_cipher_with_first_salt_key(result['cipher_id'])
            assert decrypted == test_plaintext

