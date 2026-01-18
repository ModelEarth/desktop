#!/usr/bin/env bash

# Cross-Platform Package Installer
# Detects OS and uses appropriate package manager

set -e

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGES_FILE="${SCRIPT_DIR}/desktop.conf"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            echo "linux"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Detect package manager
detect_package_manager() {
    local os=$1
    
    case "$os" in
        macos)
            if command -v brew &> /dev/null; then
                echo "brew"
            else
                echo "none"
            fi
            ;;
        linux)
            if command -v apt-get &> /dev/null; then
                echo "apt"
            elif command -v dnf &> /dev/null; then
                echo "dnf"
            elif command -v yum &> /dev/null; then
                echo "yum"
            elif command -v flatpak &> /dev/null; then
                echo "flatpak"
            else
                echo "none"
            fi
            ;;
        windows)
            if command -v winget &> /dev/null; then
                echo "winget"
            else
                echo "none"
            fi
            ;;
        *)
            echo "none"
            ;;
    esac
}

# Install Homebrew on macOS
install_homebrew() {
    log_info "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    log_success "Homebrew installed successfully"
}

# Install winget on Windows (requires manual installation)
install_winget() {
    log_error "winget is not installed. Please install it from Microsoft Store or:"
    log_info "https://github.com/microsoft/winget-cli/releases"
    exit 1
}

# Read packages from config file
read_packages() {
    local packages=()
    while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Trim whitespace
        line=$(echo "$line" | xargs)
        packages+=("$line")
    done < "$PACKAGES_FILE"
    echo "${packages[@]}"
}

# Install package based on OS and package manager
install_package() {
    local package=$1
    local os=$2
    local pkg_manager=$3
    
    log_info "Installing $package..."
    
    case "$pkg_manager" in
        brew)
            if brew list --cask "$package" &>/dev/null; then
                log_warning "$package is already installed"
            else
                brew install --cask "$package" || brew install "$package"
            fi
            ;;
        apt)
            sudo apt-get install -y "$package"
            ;;
        dnf)
            sudo dnf install -y "$package"
            ;;
        yum)
            sudo yum install -y "$package"
            ;;
        flatpak)
            flatpak install -y flathub "org.app.$package" || \
            flatpak install -y flathub "$package"
            ;;
        winget)
            winget install -e --id "$package"
            ;;
        *)
            log_error "No supported package manager found"
            exit 1
            ;;
    esac
    
    log_success "$package installed successfully"
}

# Check if package is installed
is_installed() {
    local package=$1
    local pkg_manager=$2
    
    case "$pkg_manager" in
        brew)
            brew list --cask "$package" &>/dev/null || brew list "$package" &>/dev/null
            ;;
        apt)
            dpkg -l | grep -q "^ii  $package"
            ;;
        dnf|yum)
            rpm -qa | grep -q "$package"
            ;;
        flatpak)
            flatpak list | grep -q "$package"
            ;;
        winget)
            winget list | grep -q "$package"
            ;;
        *)
            return 1
            ;;
    esac
}

# Get package version
get_version() {
    local package=$1
    local pkg_manager=$2
    
    case "$pkg_manager" in
        brew)
            brew info --cask "$package" 2>/dev/null | grep -m1 "^$package:" | awk '{print $2}' || \
            brew info "$package" 2>/dev/null | grep -m1 "^$package:" | awk '{print $2}'
            ;;
        apt)
            dpkg -l "$package" 2>/dev/null | grep "^ii" | awk '{print $3}'
            ;;
        dnf|yum)
            rpm -q "$package" 2>/dev/null | sed "s/$package-//"
            ;;
        flatpak)
            flatpak list | grep "$package" | awk '{print $2}'
            ;;
        winget)
            winget list "$package" 2>/dev/null | grep "$package" | awk '{print $2}'
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Main installation function
main() {
    log_info "Cross-Platform Package Installer v${VERSION}"
    echo ""
    
    # Detect OS
    OS=$(detect_os)
    log_info "Detected OS: $OS"
    
    # Detect package manager
    PKG_MANAGER=$(detect_package_manager "$OS")
    log_info "Package manager: $PKG_MANAGER"
    
    # Install package manager if needed
    if [ "$PKG_MANAGER" = "none" ]; then
        log_warning "No package manager found"
        if [ "$OS" = "macos" ]; then
            install_homebrew
            PKG_MANAGER="brew"
        elif [ "$OS" = "windows" ]; then
            install_winget
        else
            log_error "Please install a package manager (apt, dnf, or flatpak)"
            exit 1
        fi
    fi
    
    # Read packages
    log_info "Reading packages from $PACKAGES_FILE"
    PACKAGES=($(read_packages))
    
    if [ ${#PACKAGES[@]} -eq 0 ]; then
        log_warning "No packages enabled in $PACKAGES_FILE"
        log_info "Edit the file and uncomment packages to install"
        exit 0
    fi
    
    log_info "Found ${#PACKAGES[@]} package(s) to install"
    echo ""
    
    # Install each package
    for package in "${PACKAGES[@]}"; do
        install_package "$package" "$OS" "$PKG_MANAGER"
        echo ""
    done
    
    log_success "All packages installed successfully!"
}

# Run main function
main "$@"
