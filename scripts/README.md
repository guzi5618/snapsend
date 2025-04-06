# Snap Send Scripts

This directory contains a script to help with Snap Send installation.

## Available Script

### install_snap_send.sh

A system-wide installation script that copies Snap Send to your home directory and adds the launcher to your system path.

**Usage:**
```bash
chmod +x install_snap_send.sh
./install_snap_send.sh
```

This will:
1. Create a copy of Snap Send in `~/snap_send/` (Mac home directory)
2. Install the `snap_send` command to your system path (`/usr/local/bin/` on macOS)
3. Allow you to run `snap_send` from any directory

**Note:** On Mac computers, the installation uses macOS-specific paths. For Linux or other systems, paths may differ. 