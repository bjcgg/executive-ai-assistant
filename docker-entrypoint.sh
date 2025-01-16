#!/bin/bash
set -e

# Generate secret files from environment variables
python scripts/generate_secrets.py

# Execute the main container command
exec "$@" 