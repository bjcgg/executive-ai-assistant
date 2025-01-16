#!/bin/bash
set -e

echo "Starting entrypoint script..."

# Generate secret files from environment variables
echo "Generating secret files..."
python scripts/generate_secrets.py
echo "Secret files generated."

# Print directory contents for debugging
echo "Contents of eaia/.secrets:"
ls -la eaia/.secrets

# Execute the main container command
echo "Executing main command: $@"
exec "$@" 