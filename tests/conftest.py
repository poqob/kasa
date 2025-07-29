import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.saltService import SaltService
from src.services.cipherService import CipherService


@pytest.fixture(scope="session")
def salt_service():
    """Create a SaltService instance for testing."""
    return SaltService(config_path=".env")


@pytest.fixture(scope="session")
def cipher_service():
    """Create a CipherService instance for testing."""
    return CipherService(config_path=".env")


@pytest.fixture(scope="function")
def setup_first_salt(salt_service):
    """Ensure we have a first salt for testing."""
    try:
        # Check if first salt exists
        first_salt = salt_service.get_salt(1)
        if not first_salt:
            # Create first salt if it doesn't exist
            salt_id = salt_service.create_salt(method="sha256")
            if salt_id != 1:
                # If the created salt is not ID 1, we'll work with what we have
                pytest.skip(f"Could not create salt with ID 1, got ID {salt_id}")
        return first_salt or salt_service.get_salt(1)
    except Exception as e:
        pytest.skip(f"Could not setup first salt: {e}")


@pytest.fixture(scope="function")
def cleanup_test_ciphers(cipher_service):
    """Clean up test ciphers after each test."""
    test_cipher_ids = []
    
    def _add_cipher_id(cipher_id):
        test_cipher_ids.append(cipher_id)
    
    yield _add_cipher_id
    
    # Cleanup after test
    for cipher_id in test_cipher_ids:
        try:
            cipher_service.delete_cipher(cipher_id)
        except:
            pass  # Ignore cleanup errors


@pytest.fixture(scope="function") 
def test_data():
    """Common test data for cipher tests."""
    return [
        {"name": "test_aes256", "plaintext": "Secret message for AES256", "method": "aes256"},
        {"name": "test_aes128", "plaintext": "Secret message for AES128", "method": "aes128"},
        {"name": "test_chacha20", "plaintext": "Secret message for ChaCha20", "method": "chacha20"}
    ]


@pytest.fixture(scope="function")
def comprehensive_test_data():
    """Comprehensive test data with edge cases."""
    return [
        {
            "name": "simple_text",
            "plaintext": "Hello World!",
            "method": "aes256"
        },
        {
            "name": "empty_string", 
            "plaintext": "",
            "method": "aes128"
        },
        {
            "name": "special_chars",
            "plaintext": "!@#$%^&*()_+{}|:<>?[]\\;'\",./ àáâãäçèéêë",
            "method": "chacha20"
        },
        {
            "name": "long_text",
            "plaintext": "This is a very long text message that contains multiple sentences and should test the encryption and decryption capabilities with longer content. " * 5,
            "method": "aes256"
        },
        {
            "name": "numbers_and_symbols",
            "plaintext": "1234567890 !@#$%^&*() ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz",
            "method": "aes128"
        }
    ]
