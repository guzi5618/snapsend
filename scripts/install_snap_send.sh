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
  git clone https://github.com/yourusername/snap_send.git "$INSTALL_DIR" 2>/dev/null || {
    echo "Failed to clone from GitHub. Copying from current directory..."
    cp -r "$0/../*" "$INSTALL_DIR"
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

# Create installation directory and copy current files
mkdir -p "$HOME/snap_send"
cp -r "$CURRENT_DIR"/* "$HOME/snap_send/"

# Clean up
rm /tmp/snap_send

echo "Snap Send has been installed!"
echo "You can now run 'snap_send' from any terminal to start the service." 