import json
import os

def generate_secret_files():
    """Generate secrets.json and token.json from environment variables."""
    secrets_dir = "eaia/.secrets"
    
    # Generate secrets.json
    if os.environ.get("GMAIL_SECRET"):
        with open(f"{secrets_dir}/secrets.json", "w") as f:
            f.write(os.environ["GMAIL_SECRET"])
    
    # Generate token.json
    if os.environ.get("GMAIL_TOKEN"):
        with open(f"{secrets_dir}/token.json", "w") as f:
            f.write(os.environ["GMAIL_TOKEN"])

if __name__ == "__main__":
    generate_secret_files() 