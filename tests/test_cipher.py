
from src.services.cipherService import CipherService


def cipher_service_test():
    cipher_service = CipherService(config_path=".env")
    methods = cipher_service.get_supported_methods()
    for m in methods:
        print(f"Supported Cipher Method: {m}")


def test_first_salt_key_cipher():
    """
    Test the create_cipher_with_first_salt_key and decrypt_cipher_with_first_salt_key methods.
    """
    print("\n=== Testing First Salt Key Cipher Methods ===")
    
    try:
        cipher_service = CipherService(config_path=".env")
        
        # Step 1: Ensure we have a salt with ID 1
        print("Step 1: Checking if first salt exists...")
        try:
            first_salt = cipher_service.salt_service.get_salt(1)
            if not first_salt:
                print("First salt not found. Creating salt with ID 1...")
                salt_id = cipher_service.salt_service.create_salt(method="sha256")
                print(f"Created salt with ID: {salt_id}")
                
                # If the created salt is not ID 1, we might need to handle this
                if salt_id != 1:
                    print(f"Warning: Created salt has ID {salt_id}, not 1. Testing with existing salt...")
            else:
                print(f"First salt found: {first_salt}")
        except Exception as e:
            print(f"Error checking/creating first salt: {e}")
            return
        
        # Step 2: Test create_cipher_with_first_salt_key
        print("\nStep 2: Testing create_cipher_with_first_salt_key...")
        test_data = [
            {"name": "test_aes256", "plaintext": "Secret message for AES256", "method": "aes256"},
            {"name": "test_aes128", "plaintext": "Secret message for AES128", "method": "aes128"},
            {"name": "test_chacha20", "plaintext": "Secret message for ChaCha20", "method": "chacha20"}
        ]
        
        created_ciphers = []
        
        for test in test_data:
            try:
                result = cipher_service.create_cipher_with_first_salt_key(
                    name=test["name"],
                    plaintext=test["plaintext"],
                    method=test["method"]
                )
                created_ciphers.append(result)
                
                print(f"✓ Created cipher '{test['name']}' with method '{test['method']}':")
                print(f"  - Cipher ID: {result['cipher_id']}")
                print(f"  - Salt ID used: {result['salt_id_used']}")
                print(f"  - Cipher key used: {result['cipher_key_used']}")
                print(f"  - Original plaintext: {test['plaintext']}")
                
            except Exception as e:
                print(f"✗ Failed to create cipher '{test['name']}': {e}")
        
        # Step 3: Test decrypt_cipher_with_first_salt_key
        print("\nStep 3: Testing decrypt_cipher_with_first_salt_key...")
        
        for i, result in enumerate(created_ciphers):
            try:
                decrypted_text = cipher_service.decrypt_cipher_with_first_salt_key(
                    cipher_id=result["cipher_id"]
                )
                
                original_plaintext = test_data[i]["plaintext"]
                
                if decrypted_text == original_plaintext:
                    print(f"✓ Successfully decrypted cipher '{result['name']}':")
                    print(f"  - Cipher ID: {result['cipher_id']}")
                    print(f"  - Decrypted text: {decrypted_text}")
                    print(f"  - Match with original: YES")
                else:
                    print(f"✗ Decryption mismatch for cipher '{result['name']}':")
                    print(f"  - Expected: {original_plaintext}")
                    print(f"  - Got: {decrypted_text}")
                    
            except Exception as e:
                print(f"✗ Failed to decrypt cipher '{result['name']}' (ID: {result['cipher_id']}): {e}")
        
        # Step 4: Test error handling
        print("\nStep 4: Testing error handling...")
        try:
            # Try to decrypt a non-existent cipher
            cipher_service.decrypt_cipher_with_first_salt_key(cipher_id=99999)
        except Exception as e:
            print(f"✓ Expected error for non-existent cipher: {e}")
        
        print("\n=== First Salt Key Cipher Tests Completed ===")
        
    except Exception as e:
        print(f"✗ Test setup failed: {e}")


def test_cipher_with_first_salt_comprehensive():
    """
    Comprehensive test for first salt key cipher functionality.
    """
    print("\n=== Comprehensive First Salt Key Test ===")
    
    try:
        cipher_service = CipherService(config_path=".env")
        
        # Test with different data types and edge cases
        test_cases = [
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
        
        print(f"Running {len(test_cases)} comprehensive test cases...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['name']} ---")
            
            try:
                # Create cipher
                create_result = cipher_service.create_cipher_with_first_salt_key(
                    name=test_case["name"],
                    plaintext=test_case["plaintext"],
                    method=test_case["method"]
                )
                
                print(f"✓ Created cipher ID: {create_result['cipher_id']}")
                
                # Decrypt cipher
                decrypted = cipher_service.decrypt_cipher_with_first_salt_key(
                    cipher_id=create_result["cipher_id"]
                )
                
                # Verify match
                if decrypted == test_case["plaintext"]:
                    print(f"✓ Encryption/Decryption successful")
                    print(f"  - Method: {test_case['method']}")
                    print(f"  - Text length: {len(test_case['plaintext'])} chars")
                    if len(test_case["plaintext"]) <= 50:
                        print(f"  - Content: '{test_case['plaintext']}'")
                    else:
                        print(f"  - Content preview: '{test_case['plaintext'][:50]}...'")
                else:
                    print(f"✗ Content mismatch!")
                    print(f"  - Expected length: {len(test_case['plaintext'])}")
                    print(f"  - Got length: {len(decrypted)}")
                    
            except Exception as e:
                print(f"✗ Test case failed: {e}")
        
        print("\n=== Comprehensive Test Completed ===")
        
    except Exception as e:
        print(f"✗ Comprehensive test setup failed: {e}")

