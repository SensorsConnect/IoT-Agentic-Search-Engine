#!/bin/bash

# Path to your .env file
ENV_FILE=".env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "$ENV_FILE does not exist."
  exit 1
fi

# Export each variable in the .env file to the system environment
while IFS= read -r line || [ -n "$line" ]; do
  # Skip empty lines and comments
  if [[ ! "$line" =~ ^# && "$line" != "" ]]; then
    export $line
    # Also add the variable to the shell configuration file
    echo "export $line" >> ~/.bashrc  # Replace ~/.bashrc with ~/.zshrc if you're using zsh
  fi
done < "$ENV_FILE"

# Reload the shell configuration
source ~/.bashrc  # Replace ~/.bashrc with ~/.zshrc if you're using zsh

echo "Environment variables from $ENV_FILE have been exported to the system."
