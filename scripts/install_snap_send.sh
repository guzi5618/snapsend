#!/bin/bash

# Get the current directory of the script
CURRENT_DIR=$(pwd)

# Create the snap_send command script
cat > /tmp/snap_send << 'EOF'
#!/bin/bash

# Get the installation directory
INSTALL_DIR="$HOME/snap_send"

# Check if the installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
  echo "Snap Send is not installed. Installing now..."
  mkdir -p "$INSTALL_DIR"
  # Copy files from the script's directory
  SCRIPT_DIR="$(dirname "$0")/.."
  echo "Copying files from $SCRIPT_DIR to $INSTALL_DIR..."
  cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR" 2>/dev/null || {
    echo "Error: Could not copy files. Please check permissions."
    exit 1
  }
fi

# Go to the installation directory
cd "$INSTALL_DIR"

# Run the server
python3 snap_send_server.py

EOF

# Make the script executable
chmod +x /tmp/snap_send

# Determine where to install the command based on user's OS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  INSTALL_PATH="/usr/local/bin/snap_send"
  sudo cp /tmp/snap_send "$INSTALL_PATH"
  echo "Installing to $INSTALL_PATH (you may be asked for your password)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  INSTALL_PATH="/usr/local/bin/snap_send"
  sudo cp /tmp/snap_send "$INSTALL_PATH"
  echo "Installing to $INSTALL_PATH (you may be asked for your password)"
else
  # Other OS (Windows)
  INSTALL_PATH="$HOME/bin/snap_send"
  mkdir -p "$HOME/bin"
  cp /tmp/snap_send "$INSTALL_PATH"
  echo "Installing to $INSTALL_PATH"
  echo "You may need to add $HOME/bin to your PATH"
fi

# Clean up
rm /tmp/snap_send

echo "Snap Send has been installed!"
echo "You can now run 'snap_send' from any terminal to start the service." 