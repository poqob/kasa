from flask import Flask, request, jsonify
from src.services.saltService import SaltService
from src.services.cipherService import CipherService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize services
salt_service = SaltService(config_path=".env")
cipher_service = CipherService(config_path=".env")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Kasa API is running",
        "version": "1.0.0"
    }), 200


@app.route('/update-salt', methods=['PUT'])
def update_salt():
    """
    Update the first indexed salt (ID = 1)
    Expected JSON: {"method": "sha256", "salt_value": "optional_custom_salt"}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "JSON data required",
                "message": "Please provide method and optional salt_value"
            }), 400
        
        method = data.get('method', 'sha256')
        salt_value = data.get('salt_value')
        
        # Check if first salt exists
        first_salt = salt_service.get_salt(1)
        
        if first_salt:
            # Delete existing first salt
            salt_service.delete_salt(1)
            logger.info("Deleted existing first salt")
        
        # Create new first salt
        salt_id = salt_service.create_salt(method=method, salt_value=salt_value)
        
        if salt_id == 1:
            updated_salt = salt_service.get_salt(1)
            logger.info(f"Updated first salt with method: {method}")
            
            return jsonify({
                "success": True,
                "message": "First salt updated successfully",
                "salt_info": {
                    "id": updated_salt['id'],
                    "method": updated_salt['method'],
                    "salt": updated_salt['salt'][:20] + "..." if len(updated_salt['salt']) > 20 else updated_salt['salt']
                }
            }), 200
        else:
            logger.warning(f"Created salt with ID {salt_id} instead of 1")
            return jsonify({
                "success": True,
                "message": f"Salt created with ID {salt_id} (not 1)",
                "salt_id": salt_id
            }), 200
            
    except Exception as e:
        logger.error(f"Error updating salt: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/set-cipher', methods=['POST'])
def set_cipher():
    """
    Create a new cipher using first indexed salt
    Expected JSON: {"name": "cipher_name", "plaintext": "text_to_encrypt", "method": "aes256"}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "JSON data required",
                "message": "Please provide name, plaintext, and optional method"
            }), 400
        
        name = data.get('name')
        plaintext = data.get('plaintext')
        method = data.get('method', 'aes256')
        
        if not name or not plaintext:
            return jsonify({
                "error": "Missing required fields",
                "message": "name and plaintext are required"
            }), 400
        
        # Create cipher using first salt key
        result = cipher_service.create_cipher_with_first_salt_key(
            name=name,
            plaintext=plaintext,
            method=method
        )
        
        logger.info(f"Created cipher '{name}' with ID {result['cipher_id']}")
        
        return jsonify({
            "success": True,
            "message": "Cipher created successfully",
            "cipher_info": {
                "cipher_id": result['cipher_id'],
                "name": result['name'],
                "method": result['cipher_method'],
                "salt_id_used": result['salt_id_used'],
                "cipher_key_used": result['cipher_key_used']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating cipher: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/get-cipher-by-name/<cipher_name>', methods=['GET'])
def get_cipher_by_name(cipher_name):
    """
    Get and decrypt cipher by name using first indexed salt
    URL parameter: cipher_name
    """
    try:
        if not cipher_name or cipher_name.strip() == "":
            return jsonify({
                "error": "Invalid cipher name",
                "message": "Cipher name cannot be empty"
            }), 400
        
        # Decrypt cipher by name using first salt key
        result = cipher_service.decrypt_cipher_by_name_with_first_salt_key(cipher_name)
        
        logger.info(f"Successfully decrypted cipher '{result['cipher_name']}'")
        
        return jsonify({
            "success": True,
            "message": "Cipher found and decrypted successfully",
            "result": {
                "decrypted_text": result['decrypted_text'],
                "cipher_name": result['cipher_name'],
                "cipher_id": result['cipher_id'],
                "method": result['method'],
                "search_term": result['search_term'],
                "matches_found": result['matches_found']
            }
        }), 200
        
    except ValueError as ve:
        error_msg = str(ve)
        
        if "Multiple ciphers found" in error_msg:
            # Extract suggestions from error message or get them separately
            try:
                suggestions = cipher_service.get_cipher_suggestions_by_name(cipher_name)
                return jsonify({
                    "error": "Multiple matches found",
                    "message": f"Multiple ciphers found with name containing '{cipher_name}'",
                    "suggestions": suggestions
                }), 400
            except:
                return jsonify({
                    "error": "Multiple matches found",
                    "message": error_msg
                }), 400
                
        elif "No ciphers found" in error_msg:
            return jsonify({
                "error": "Cipher not found",
                "message": f"No ciphers found containing '{cipher_name}'"
            }), 404
        else:
            return jsonify({
                "error": "Validation error",
                "message": error_msg
            }), 400
            
    except Exception as e:
        logger.error(f"Error getting cipher by name: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/delete-cipher-by-name/<cipher_name>', methods=['DELETE'])
def delete_cipher_by_name(cipher_name):
    """
    Delete cipher by name
    URL parameter: cipher_name
    """
    try:
        if not cipher_name or cipher_name.strip() == "":
            return jsonify({
                "error": "Invalid cipher name",
                "message": "Cipher name cannot be empty"
            }), 400
        
        # Search for cipher by name
        matching_ciphers = cipher_service.search_ciphers_by_name(cipher_name)
        
        if not matching_ciphers:
            return jsonify({
                "error": "Cipher not found",
                "message": f"No ciphers found containing '{cipher_name}'"
            }), 404
        
        if len(matching_ciphers) > 1:
            # Multiple matches found - return suggestions
            suggestions = []
            for cipher in matching_ciphers:
                suggestions.append({
                    "id": cipher["id"],
                    "name": cipher["name"],
                    "method": cipher["method"]
                })
            
            return jsonify({
                "error": "Multiple matches found",
                "message": f"Multiple ciphers found with name containing '{cipher_name}'. Please be more specific.",
                "suggestions": suggestions
            }), 400
        
        # Single match found - delete it
        cipher = matching_ciphers[0]
        cipher_id = cipher["id"]
        cipher_name_found = cipher["name"]
        
        success = cipher_service.delete_cipher(cipher_id)
        
        if success:
            logger.info(f"Deleted cipher '{cipher_name_found}' (ID: {cipher_id})")
            return jsonify({
                "success": True,
                "message": f"Cipher '{cipher_name_found}' deleted successfully",
                "deleted_cipher": {
                    "id": cipher_id,
                    "name": cipher_name_found,
                    "method": cipher["method"]
                }
            }), 200
        else:
            return jsonify({
                "error": "Deletion failed",
                "message": f"Failed to delete cipher '{cipher_name_found}'"
            }), 500
            
    except Exception as e:
        logger.error(f"Error deleting cipher by name: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/ciphers', methods=['GET'])
def list_ciphers():
    """
    List all ciphers (bonus endpoint)
    """
    try:
        ciphers = cipher_service.list_all_ciphers()
        
        return jsonify({
            "success": True,
            "message": f"Found {len(ciphers)} cipher(s)",
            "ciphers": ciphers
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing ciphers: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/salts', methods=['GET'])
def list_salts():
    """
    List all salts (bonus endpoint)
    """
    try:
        salts = salt_service.list_all_salts()
        
        # Hide full salt values for security
        secure_salts = []
        for salt in salts:
            secure_salt = salt.copy()
            secure_salt['salt'] = secure_salt['salt'][:10] + "..." if len(secure_salt['salt']) > 10 else secure_salt['salt']
            secure_salts.append(secure_salt)
        
        return jsonify({
            "success": True,
            "message": f"Found {len(secure_salts)} salt(s)",
            "salts": secure_salts
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing salts: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed",
        "message": "The HTTP method is not allowed for this endpoint"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    print("Starting Kasa API Server...")
    print("Available endpoints:")
    print("  PUT    /update-salt")
    print("  POST   /set-cipher") 
    print("  GET    /get-cipher-by-name/<name>")
    print("  DELETE /delete-cipher-by-name/<name>")
    print("  GET    /ciphers (bonus)")
    print("  GET    /salts (bonus)")
    print("  GET    /health")
    print("=" * 50)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )