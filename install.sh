#!/bin/bash

#  _____                         _     
# |  _  |___ ___ ___ ___ ___ ___| |___ 
# |     |  _|  _| .'|   | . | -_| | . |
#|__|__|_| |___|__,|_|_|_  |___|_|___|
                      |___|          
                      
# NekoCLI Installer
set -e
echo "🐱 Installing NekoCLI..."
INSTALL_DIR="$HOME/nekoCLI"
if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
fi
cp -r modules "$INSTALL_DIR/"
cp -r utils "$INSTALL_DIR/"
cp config.py "$INSTALL_DIR/"
cp init.py "$INSTALL_DIR/"
cp neko "$INSTALL_DIR/neko"
chmod +x "$INSTALL_DIR/neko"
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.bashrc"  # fallback
fi

if [ -f "$SHELL_RC" ]; then
    if ! grep -q "export PATH=\"$INSTALL_DIR:\$PATH\"" "$SHELL_RC"; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
        echo "Added $INSTALL_DIR to PATH in $SHELL_RC"
        echo "Please run 'source $SHELL_RC' or restart your terminal to use neko"
    else
        echo "$INSTALL_DIR already in PATH"
    fi
fi
echo "✅😼 NekoCLI installed successfully!"
echo "---------------------------------------"
echo "> You can now use 'neko' from anywhere in your terminal."
echo "[+] Installation directory: $INSTALL_DIR"
