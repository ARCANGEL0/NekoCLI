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
if ! command -v glow &>/dev/null; then
    echo "📦 Installing glow (markdown renderer)..."
    # Linux package managers
    if command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm glow
    elif command -v apt-get &>/dev/null; then
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
        echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
        sudo apt-get update && sudo apt-get install -y glow
    elif command -v dnf &>/dev/null; then
        echo -e '[charm]\nname=Charm\nbaseurl=https://repo.charm.sh/yum/\nenabled=1\ngpgcheck=1\ngpgkey=https://repo.charm.sh/yum/gpg.key' | sudo tee /etc/yum.repos.d/charm.repo
        sudo dnf install -y glow
    # macOS
    elif command -v brew &>/dev/null; then
        brew install glow
    # Windows / Windows shells
    elif command -v choco &>/dev/null; then
        echo "Using Chocolatey to install glow..."
        choco install glow -y || echo "Chocolatey installation failed. Please install glow manually from https://github.com/charmbracelet/glow/releases"
    elif command -v winget &>/dev/null; then
        echo "Using winget to install glow..."
        # try common uses for windows stf
        winget install --id Charm.Glow -e || winget install glow || echo "winget installation failed. Please install glow manually from https://github.com/charmbracelet/glow/releases"
    elif command -v scoop &>/dev/null; then
        echo "Using Scoop to install glow..."
        scoop install glow || echo "Scoop installation failed. Please install glow manually from https://github.com/charmbracelet/glow/releases"
    else
			# allfailed
        UNAME="$(uname -s 2>/dev/null || echo)">
        if [ "${OS:-}" = "Windows_NT" ] || echo "$UNAME" | grep -Eiq "MINGW|MSYS|CYGWIN|Windows"; then
            echo "⚠️  No Windows package manager detected (choco, winget or scoop)."
            echo "   Please install glow manually: https://github.com/charmbracelet/glow/releases"
            echo "   Or install Chocolatey: https://chocolatey.org/install or Winget: https://learn.microsoft.com/windows/package-manager/winget/"
        else
            echo "⚠️  Could not install glow automatically."
            echo "   Install manually: https://github.com/charmbracelet/glow/releases"
        fi
    fi
else
    echo "✔ glow already installed"
fi

echo "✅😼 NekoCLI installed successfully!"
echo "---------------------------------------"
echo "> You can now use 'neko' from anywhere in your terminal."
echo "[+] Installation directory: $INSTALL_DIR"
