import json
import os

def generate_secrets():
    """Generate secrets.json and token.json from environment variables."""
    secrets_dir = os.path.join(os.path.dirname(__file__), ".secrets")
    
    # Ensure secrets directory exists
    os.makedirs(secrets_dir, exist_ok=True)
    
    # Generate secrets.json
    if os.environ.get("GMAIL_SECRET"):
        with open(os.path.join(secrets_dir, "secrets.json"), "w") as f:
            f.write(os.environ["GMAIL_SECRET"])
    
    # Generate token.json
    if os.environ.get("GMAIL_TOKEN"):
        with open(os.path.join(secrets_dir, "token.json"), "w") as f:
            f.write(os.environ["GMAIL_TOKEN"])

if __name__ == "__main__":
    generate_secrets() 