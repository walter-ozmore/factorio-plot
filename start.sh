#!/bin/bash

set -e # Set -e to exit on first error

# rm -r venv # Remove the Python env for testing

# Create python env when it doesn't exist
if [[ ! -d venv ]]; then
  echo "Creating Python env"
  python3 -m venv venv
	source venv/bin/activate
	pip install pyyaml pillow requests
else
	source venv/bin/activate
fi

# Run our python script
clear
python3 draw-image.py