from stellar_sdk import Keypair

def generate_stellar_keypair():
    # Generate a random keypair
    keypair = Keypair.random()
    
    # Get the public and secret keys
    public_key = keypair.public_key
    secret_key = keypair.secret
    
    # Print the keypair
    print("New Stellar Wallet Keypair Generated:")
    print(f"Public Key: {public_key}")
    print(f"Secret Key: {secret_key}")
    print("\nWARNING: Save your secret key securely! Do NOT share it.")
    
    # Optionally save to a file
    try:
        with open("stellar_keypair.txt", "w") as f:
            f.write(f"Public Key: {public_key}\n")
            f.write(f"Secret Key: {secret_key}\n")
        print("Keypair saved to 'stellar_keypair.txt'")
    except Exception as e:
        print(f"Failed to save keypair to file: {e}")

if __name__ == "__main__":
    generate_stellar_keypair()