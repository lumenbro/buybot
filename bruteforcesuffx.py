from stellar_sdk import Keypair

def generate_stellar_keypair_with_suffix(desired_suffix):
    """
    Generate a Stellar keypair with a public key ending in the specified suffix.
    The suffix must be valid Base32 characters (A-Z, 2-7).
    """
    desired_suffix = desired_suffix.upper()  # Ensure uppercase for Base32
    valid_base32_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
    
    # Validate suffix
    if not all(c in valid_base32_chars for c in desired_suffix):
        raise ValueError("Suffix contains invalid Base32 characters. Use A-Z or 2-7.")
    
    attempt_count = 0
    while True:
        attempt_count += 1
        # Generate a random keypair
        keypair = Keypair.random()
        public_key = keypair.public_key
        secret_key = keypair.secret
        
        # Check if public key ends with desired suffix
        if public_key.endswith(desired_suffix):
            # Print the matching keypair
            print("\nFound matching Stellar Wallet Keypair:")
            print(f"Public Key: {public_key}")
            print(f"Secret Key: {secret_key}")
            print("\nWARNING: Save your secret key securely! Do NOT share it.")
            print(f"Attempts made: {attempt_count}")
            
            # Optionally save to a file
            try:
                with open("stellar_keypair.txt", "w") as f:
                    f.write(f"Public Key: {public_key}\n")
                    f.write(f"Secret Key: {secret_key}\n")
                print("Keypair saved to 'stellar_keypair.txt'")
            except Exception as e:
                print(f"Failed to save keypair to file: {e}")
            
            return public_key, secret_key
        
        # Print progress every 1000 attempts
        if attempt_count % 1000 == 0:
            print(f"Attempts: {attempt_count}, still searching for suffix '{desired_suffix}'...")

if __name__ == "__main__":
    # Specify the desired suffix (e.g., "LUMEN", "BRO", "LB")
    desired_suffix = "BRO"  # Change this to "LUMEN", "BRO", or any valid Base32 suffix
    try:
        generate_stellar_keypair_with_suffix(desired_suffix)
    except ValueError as e:
        print(f"Error: {e}")