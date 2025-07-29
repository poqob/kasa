from src.services.saltService import SaltService
from src.services.cipherService import CipherService
import os
import sys


class KasaCLI:
    """
    Command Line Interface for Kasa - Password and Cipher Management System
    """
    
    def __init__(self):
        self.salt_service = SaltService(config_path=".env")
        self.cipher_service = CipherService(config_path=".env")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print the application header"""
        print("=" * 60)
        print("🔐 KASA - Password & Cipher Management System")
        print("=" * 60)
    
    def print_menu(self):
        """Print the main menu options"""
        print("\n📋 MAIN MENU:")
        print("1.  🧂 Salt Management")
        print("2.  🔒 Cipher Management") 
        print("3.  🔑 First Salt Key Cipher")
        print("4.  📊 System Information")
        print("5.  🧪 Run Tests")
        print("0.  ❌ Exit")
        print("-" * 40)
    
    def print_salt_menu(self):
        """Print salt management menu"""
        print("\n🧂 SALT MANAGEMENT:")
        print("1.  Create New Salt")
        print("2.  List All Salts")
        print("3.  Get Salt by ID")
        print("4.  Delete Salt")
        print("5.  Generate Salt for Key")
        print("6.  Get Supported Methods")
        print("0.  ← Back to Main Menu")
        print("-" * 40)
    
    def print_cipher_menu(self):
        """Print cipher management menu"""
        print("\n🔒 CIPHER MANAGEMENT:")
        print("1.  Create New Cipher")
        print("2.  List All Ciphers")
        print("3.  Get Cipher by ID")
        print("4.  Decrypt Cipher by ID")
        print("5.  Decrypt Cipher by Name")
        print("6.  Update Cipher")
        print("7.  Delete Cipher")
        print("8.  Search Ciphers by Name")
        print("9.  Encrypt and Store")
        print("0.  ← Back to Main Menu")
        print("-" * 40)
    
    def print_first_salt_menu(self):
        """Print first salt key cipher menu"""
        print("\n🔑 FIRST SALT KEY CIPHER:")
        print("1.  Create Cipher with First Salt Key")
        print("2.  Decrypt Cipher with First Salt Key")
        print("0.  ← Back to Main Menu")
        print("-" * 40)
    
    def get_user_input(self, prompt: str) -> str:
        """Get user input with prompt"""
        return input(f"👤 {prompt}: ").strip()
    
    def get_user_choice(self) -> str:
        """Get user menu choice"""
        return input("🎯 Enter your choice: ").strip()
    
    def pause(self):
        """Pause for user to read output"""
        input("\n⏸️  Press Enter to continue...")
    
    def handle_error(self, error):
        """Handle and display errors"""
        print(f"❌ Error: {error}")
        self.pause()
    
    # Salt Management Functions
    def create_salt(self):
        """Create a new salt"""
        try:
            print("\n🧂 CREATE NEW SALT")
            method = self.get_user_input("Enter salt method (sha256/sha512/md5/argon2) [default: sha256]") or "sha256"
            salt_value = self.get_user_input("Enter custom salt value (optional, press Enter for random)")
            
            if not salt_value:
                salt_value = None
            
            salt_id = self.salt_service.create_salt(method=method, salt_value=salt_value)
            print(f"✅ Salt created successfully with ID: {salt_id}")
            
        except Exception as e:
            self.handle_error(e)
    
    def list_salts(self):
        """List all salts"""
        try:
            print("\n🧂 ALL SALTS:")
            salts = self.salt_service.list_all_salts()
            
            if not salts:
                print("📭 No salts found.")
            else:
                for salt in salts:
                    print(f"ID: {salt['id']}, Method: {salt['method']}, Salt: {salt['salt'][:20]}...")
            
        except Exception as e:
            self.handle_error(e)
    
    def get_salt(self):
        """Get salt by ID"""
        try:
            print("\n🧂 GET SALT BY ID")
            salt_id = int(self.get_user_input("Enter salt ID"))
            
            salt = self.salt_service.get_salt(salt_id)
            if salt:
                print(f"✅ Salt found:")
                print(f"   ID: {salt['id']}")
                print(f"   Method: {salt['method']}")
                print(f"   Salt: {salt['salt']}")
            else:
                print("❌ Salt not found.")
                
        except ValueError:
            print("❌ Invalid salt ID. Please enter a number.")
        except Exception as e:
            self.handle_error(e)
    
    def delete_salt(self):
        """Delete salt by ID"""
        try:
            print("\n🧂 DELETE SALT")
            salt_id = int(self.get_user_input("Enter salt ID to delete"))
            
            confirm = self.get_user_input(f"Are you sure you want to delete salt {salt_id}? (yes/no)")
            if confirm.lower() in ['yes', 'y']:
                success = self.salt_service.delete_salt(salt_id)
                if success:
                    print("✅ Salt deleted successfully.")
                else:
                    print("❌ Salt not found or deletion failed.")
            else:
                print("🚫 Deletion cancelled.")
                
        except ValueError:
            print("❌ Invalid salt ID. Please enter a number.")
        except Exception as e:
            self.handle_error(e)
    
    def generate_salt_for_key(self):
        """Generate salt for a key"""
        try:
            print("\n🧂 GENERATE SALT FOR KEY")
            secret_key = self.get_user_input("Enter secret key")
            method = self.get_user_input("Enter salt method [default: sha256]") or "sha256"
            
            result = self.salt_service.generate_salt_for_key(secret_key, method)
            print(f"✅ Salt generated and applied:")
            print(f"   Salt ID: {result['salt_id']}")
            print(f"   Method: {result['method']}")
            print(f"   Salted Key: {result['salted_key']}")
            
        except Exception as e:
            self.handle_error(e)
    
    def get_salt_methods(self):
        """Get supported salt methods"""
        try:
            print("\n🧂 SUPPORTED SALT METHODS:")
            methods = self.salt_service.get_supported_methods()
            for method in methods:
                print(f"   • {method}")
                
        except Exception as e:
            self.handle_error(e)
    
    # Cipher Management Functions
    def create_cipher(self):
        """Create a new cipher using first salt key automatically"""
        try:
            print("\n🔒 CREATE NEW CIPHER (Using First Salt Key)")
            name = self.get_user_input("Enter cipher name")
            plaintext = self.get_user_input("Enter plaintext to encrypt")
            method = self.get_user_input("Enter encryption method (aes128/aes256/chacha20) [default: aes256]") or "aes256"
            
            # Use first salt key automatically instead of requesting from user
            result = self.cipher_service.create_cipher_with_first_salt_key(name=name, plaintext=plaintext, method=method)
            print(f"✅ Cipher created successfully:")
            print(f"   Cipher ID: {result['cipher_id']}")
            print(f"   Salt ID used: {result['salt_id_used']}")
            print(f"   Method: {result['cipher_method']}")
            print(f"   🔑 Key: Automatically used first salt key (ID: {result['salt_id_used']})")
            
        except Exception as e:
            self.handle_error(e)
    
    def list_ciphers(self):
        """List all ciphers"""
        try:
            print("\n🔒 ALL CIPHERS:")
            ciphers = self.cipher_service.list_all_ciphers()
            
            if not ciphers:
                print("📭 No ciphers found.")
            else:
                for cipher in ciphers:
                    print(f"ID: {cipher['id']}, Name: {cipher['name']}, Method: {cipher['method']}")
            
        except Exception as e:
            self.handle_error(e)
    
    def get_cipher(self):
        """Get cipher by ID"""
        try:
            print("\n🔒 GET CIPHER BY ID")
            cipher_id = int(self.get_user_input("Enter cipher ID"))
            
            cipher = self.cipher_service.get_cipher(cipher_id)
            if cipher:
                print(f"✅ Cipher found:")
                print(f"   ID: {cipher['id']}")
                print(f"   Name: {cipher['name']}")
                print(f"   Method: {cipher['method']}")
                print(f"   Encrypted: {cipher['encrypted_cipher'][:50]}...")
            else:
                print("❌ Cipher not found.")
                
        except ValueError:
            print("❌ Invalid cipher ID. Please enter a number.")
        except Exception as e:
            self.handle_error(e)
    
    def decrypt_cipher(self):
        """Decrypt a cipher using first salt key automatically"""
        try:
            print("\n🔒 DECRYPT CIPHER (Using First Salt Key)")
            cipher_id = int(self.get_user_input("Enter cipher ID"))
            
            # Use first salt key automatically instead of requesting from user
            plaintext = self.cipher_service.decrypt_cipher_with_first_salt_key(cipher_id)
            print(f"✅ Decrypted text: {plaintext}")
            print(f"   🔑 Key: Automatically used first salt key (ID: 1)")
            
        except ValueError:
            print("❌ Invalid cipher ID. Please enter a number.")
        except Exception as e:
            self.handle_error(e)
    
    def decrypt_cipher_by_name(self):
        """Decrypt a cipher by searching for it by name using first salt key"""
        try:
            print("\n🔒 DECRYPT CIPHER BY NAME (Using First Salt Key)")
            cipher_name = self.get_user_input("Enter cipher name to search and decrypt")
            
            # Use the new service method to search and decrypt by name
            result = self.cipher_service.decrypt_cipher_by_name_with_first_salt_key(cipher_name)
            
            # Display successful result
            print(f"✅ Cipher found and decrypted successfully:")
            print(f"   Cipher Name: {result['cipher_name']}")
            print(f"   Cipher ID: {result['cipher_id']}")
            print(f"   Method: {result['method']}")
            print(f"   Decrypted Text: {result['decrypted_text']}")
            print(f"   🔑 Key: Automatically used first salt key (ID: 1)")
            print(f"   Search Term: '{result['search_term']}'")
            
        except ValueError as ve:
            # Handle specific cases like no matches or multiple matches
            error_msg = str(ve)
            if "Multiple ciphers found" in error_msg:
                print("❌ Multiple ciphers found with that name pattern.")
                print("Please be more specific or use one of these suggestions:")
                
                # Try to get suggestions
                try:
                    suggestions = self.cipher_service.get_cipher_suggestions_by_name(cipher_name)
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"   {i}. {suggestion['name']} (ID: {suggestion['id']}, Method: {suggestion['method']})")
                    
                    print("\n💡 Tip: Use the exact cipher name or a more specific search term.")
                    
                except Exception:
                    print("   Unable to get suggestions. Try using 'Search Ciphers by Name' first.")
                    
            elif "No ciphers found" in error_msg:
                print(f"❌ No ciphers found containing '{cipher_name}'")
                print("💡 Tips:")
                print("   • Check the spelling")
                print("   • Try a partial name")
                print("   • Use 'List All Ciphers' to see available ciphers")
            else:
                print(f"❌ Error: {error_msg}")
                
        except Exception as e:
            self.handle_error(e)
    
    def delete_cipher(self):
        """Delete cipher by ID"""
        try:
            print("\n🔒 DELETE CIPHER")
            cipher_id = int(self.get_user_input("Enter cipher ID to delete"))
            
            confirm = self.get_user_input(f"Are you sure you want to delete cipher {cipher_id}? (yes/no)")
            if confirm.lower() in ['yes', 'y']:
                success = self.cipher_service.delete_cipher(cipher_id)
                if success:
                    print("✅ Cipher deleted successfully.")
                else:
                    print("❌ Cipher not found or deletion failed.")
            else:
                print("🚫 Deletion cancelled.")
                
        except ValueError:
            print("❌ Invalid cipher ID. Please enter a number.")
        except Exception as e:
            self.handle_error(e)
    
    def search_ciphers(self):
        """Search ciphers by name"""
        try:
            print("\n🔒 SEARCH CIPHERS BY NAME")
            pattern = self.get_user_input("Enter name pattern to search")
            
            ciphers = self.cipher_service.search_ciphers_by_name(pattern)
            if ciphers:
                print(f"✅ Found {len(ciphers)} cipher(s):")
                for cipher in ciphers:
                    print(f"   ID: {cipher['id']}, Name: {cipher['name']}, Method: {cipher['method']}")
            else:
                print("❌ No ciphers found matching the pattern.")
                
        except Exception as e:
            self.handle_error(e)
    
    def encrypt_and_store(self):
        """Encrypt and store using first salt key automatically"""
        try:
            print("\n🔒 ENCRYPT AND STORE (Using First Salt Key)")
            name = self.get_user_input("Enter cipher name")
            plaintext = self.get_user_input("Enter plaintext to encrypt")
            method = self.get_user_input("Enter encryption method [default: aes256]") or "aes256"
            
            # Use first salt key automatically instead of requesting from user
            result = self.cipher_service.create_cipher_with_first_salt_key(name=name, plaintext=plaintext, method=method)
            print(f"✅ Cipher encrypted and stored:")
            print(f"   Cipher ID: {result['cipher_id']}")
            print(f"   Method: {result['cipher_method']}")
            print(f"   Name: {result['name']}")
            print(f"   🔑 Key: Automatically used first salt key (ID: {result['salt_id_used']})")
            
        except Exception as e:
            self.handle_error(e)
    
    # First Salt Key Cipher Functions
    def create_first_salt_cipher(self):
        """Create cipher with first salt key"""
        try:
            print("\n🔑 CREATE CIPHER WITH FIRST SALT KEY")
            name = self.get_user_input("Enter cipher name")
            plaintext = self.get_user_input("Enter plaintext to encrypt")
            method = self.get_user_input("Enter encryption method [default: aes256]") or "aes256"
            
            result = self.cipher_service.create_cipher_with_first_salt_key(name=name, plaintext=plaintext, method=method)
            print(f"✅ Cipher created with first salt key:")
            print(f"   Cipher ID: {result['cipher_id']}")
            print(f"   Salt ID used: {result['salt_id_used']}")
            print(f"   Method: {result['cipher_method']}")
            
        except Exception as e:
            self.handle_error(e)
    
    def decrypt_first_salt_cipher(self):
        """Decrypt cipher with first salt key"""
        try:
            print("\n🔑 DECRYPT CIPHER WITH FIRST SALT KEY")
            cipher_id = int(self.get_user_input("Enter cipher ID"))
            
            plaintext = self.cipher_service.decrypt_cipher_with_first_salt_key(cipher_id)
            print(f"✅ Decrypted text: {plaintext}")
            
        except ValueError:
            print("❌ Invalid cipher ID. Please enter a number.")
        except Exception as e:
            self.handle_error(e)
    
    # System Information
    def show_system_info(self):
        """Show system information"""
        try:
            print("\n📊 SYSTEM INFORMATION:")
            
            # Salt methods
            salt_methods = self.salt_service.get_supported_methods()
            print(f"🧂 Supported Salt Methods: {', '.join(salt_methods)}")
            
            # Cipher methods
            cipher_methods = self.cipher_service.get_supported_methods()
            print(f"🔒 Supported Cipher Methods: {', '.join(cipher_methods)}")
            
            # Count totals
            try:
                all_salts = self.salt_service.list_all_salts()
                print(f"🧂 Total Salts: {len(all_salts)}")
            except:
                print("🧂 Total Salts: Unable to count")
            
            try:
                all_ciphers = self.cipher_service.list_all_ciphers()
                print(f"🔒 Total Ciphers: {len(all_ciphers)}")
            except:
                print("🔒 Total Ciphers: Unable to count")
            
        except Exception as e:
            self.handle_error(e)
    
    def run_tests(self):
        """Run basic tests"""
        try:
            print("\n🧪 RUNNING BASIC TESTS...")
            
            # Test salt service
            print("Testing Salt Service...")
            methods = self.salt_service.get_supported_methods()
            print(f"✅ Salt methods: {methods}")
            
            # Test cipher service
            print("Testing Cipher Service...")
            methods = self.cipher_service.get_supported_methods()
            print(f"✅ Cipher methods: {methods}")
            
            print("✅ Basic tests completed successfully!")
            
        except Exception as e:
            self.handle_error(e)
    
    # Menu Handlers
    def handle_salt_menu(self):
        """Handle salt management menu"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_salt_menu()
            
            choice = self.get_user_choice()
            
            if choice == "1":
                self.create_salt()
                self.pause()
            elif choice == "2":
                self.list_salts()
                self.pause()
            elif choice == "3":
                self.get_salt()
                self.pause()
            elif choice == "4":
                self.delete_salt()
                self.pause()
            elif choice == "5":
                self.generate_salt_for_key()
                self.pause()
            elif choice == "6":
                self.get_salt_methods()
                self.pause()
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice. Please try again.")
                self.pause()
    
    def handle_cipher_menu(self):
        """Handle cipher management menu"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_cipher_menu()
            
            choice = self.get_user_choice()
            
            if choice == "1":
                self.create_cipher()
                self.pause()
            elif choice == "2":
                self.list_ciphers()
                self.pause()
            elif choice == "3":
                self.get_cipher()
                self.pause()
            elif choice == "4":
                self.decrypt_cipher()
                self.pause()
            elif choice == "5":
                self.decrypt_cipher_by_name()
                self.pause()
            elif choice == "6":
                print("🚧 Update cipher functionality - Coming soon!")
                self.pause()
            elif choice == "7":
                self.delete_cipher()
                self.pause()
            elif choice == "8":
                self.search_ciphers()
                self.pause()
            elif choice == "9":
                self.encrypt_and_store()
                self.pause()
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice. Please try again.")
                self.pause()
    
    def handle_first_salt_menu(self):
        """Handle first salt key cipher menu"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_first_salt_menu()
            
            choice = self.get_user_choice()
            
            if choice == "1":
                self.create_first_salt_cipher()
                self.pause()
            elif choice == "2":
                self.decrypt_first_salt_cipher()
                self.pause()
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice. Please try again.")
                self.pause()
    
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            choice = self.get_user_choice()
            
            if choice == "1":
                self.handle_salt_menu()
            elif choice == "2":
                self.handle_cipher_menu()
            elif choice == "3":
                self.handle_first_salt_menu()
            elif choice == "4":
                self.show_system_info()
                self.pause()
            elif choice == "5":
                self.run_tests()
                self.pause()
            elif choice == "0":
                print("👋 Thank you for using Kasa! Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please try again.")
                self.pause()


if __name__ == "__main__":
    try:
        cli = KasaCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)