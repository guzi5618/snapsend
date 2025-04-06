#!/bin/bash

# Get the current directory of the script
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="$HOME/snap_send"

echo "Installing Snap Send to $INSTALL_DIR"

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
  mkdir -p "$INSTALL_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create directory $INSTALL_DIR. Check permissions."
    exit 1
  fi
fi

# Copy files to the installation directory
echo "Copying files from $SCRIPT_DIR to $INSTALL_DIR"
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Error: Failed to copy files. Check permissions."
  exit 1
fi

# Create the snap_send command script
cat > /tmp/snap_send << 'EOF'
#!/bin/bash

# Get the installation directory
INSTALL_DIR="$HOME/snap_send"

# Check if the installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
  echo "Error: Snap Send is not installed at $INSTALL_DIR."
  echo "Please install Snap Send first."
  exit 1
fi

# Go to the installation directory
cd "$INSTALL_DIR"

# Check if the server script exists
if [ ! -f "snap_send_server.py" ]; then
  echo "Error: snap_send_server.py not found in $INSTALL_DIR"
  exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
  echo "Error: Python 3 is not installed. Please install Python 3 and try again."
  exit 1
fi

# Start the server
echo "Starting Snap Send server..."
python3 snap_send_server.py "$@"
EOF

# Make the script executable
chmod +x /tmp/snap_send

# Determine where to install the command based on user's OS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  INSTALL_PATH="/usr/local/bin/snap_send"
  echo "Installing to $INSTALL_PATH (you may be asked for your password)"
  sudo cp /tmp/snap_send "$INSTALL_PATH"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  INSTALL_PATH="/usr/local/bin/snap_send"
  echo "Installing to $INSTALL_PATH (you may be asked for your password)"
  sudo cp /tmp/snap_send "$INSTALL_PATH"
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