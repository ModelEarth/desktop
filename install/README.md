# Desktop Production Suite Installer

A web-based interface for managing software installations across Mac, Windows, and Linux.

**[View Installer Online](https://dreamstudio.com/desktop/install)**

## Quick Start

The fastest way to get started:

**Mac/Linux:**
```bash
cd desktop/install
chmod +x quickstart.sh setup.sh server.py  # Make scripts executable
./quickstart.sh
```

**Windows (Command Prompt or PowerShell):**
```cmd
cd desktop\install
python quickstart.sh
```

**Any Platform (without changing permissions):**
```bash
cd desktop/install
bash quickstart.sh  # or: python quickstart.sh
```

The `quickstart.sh` script is **optional** but provides an interactive setup wizard that:
- Checks Python installation
- Verifies/creates .env configuration
- Installs optional dependencies (anthropic package)
- Sets correct file permissions
- Optionally starts the server immediately

You can skip it and run the server directly if you prefer:
```bash
python3 server.py  # Mac/Linux
python server.py   # Windows
```

## Prerequisites

### All Platforms
- Python 3.6 or higher
- Internet connection
- Web browser

### Platform-Specific

**macOS:**
- Homebrew (will be installed automatically if not present)

**Windows:**
- winget (Windows Package Manager)
- Run PowerShell as Administrator for installations

**Linux:**
- One of: apt, dnf, yum, or flatpak

## Installation Steps

### 1. Download Files

Extract the `desktop/install` folder to your preferred location.

### 2. Configure Packages

Edit `desktop.conf` to select which packages you want available:

```conf
## Comments start with double ##
libreoffice # Office Suite
# blender # 3D Graphics (disabled)
```

- Lines starting with `##` are true comments (ignored)
- Lines starting with `#` are disabled packages  
- Remove the `#` to enable a package
- Add inline descriptions after the package name with `#`

### 3. Configure LLM (Optional)

If you want AI-powered modifications:

1. Get an Anthropic API key from https://console.anthropic.com/
2. Create `.env` file at `../../docker/.env`:

```bash
# From the desktop/install directory
mkdir -p ../../docker
cp .env.example ../../docker/.env
```

3. Edit `../../docker/.env` and add your key:

```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

4. Install the anthropic package:

```bash
pip install anthropic
```

Or on systems requiring break-system-packages:

```bash
pip install anthropic --break-system-packages
```

### 4. Start the Server

**Mac/Linux:**
```bash
cd desktop/install
chmod +x server.py setup.sh quickstart.sh  # Make executable (one-time only)
python3 server.py
```

**Windows:**
```cmd
cd desktop\install
python server.py
```

**Custom Port:**
```bash
python3 server.py --port 8080  # Mac/Linux
python server.py --port 8080   # Windows
```

**Verbose Logging:**
```bash
python3 server.py --verbose  # Mac/Linux
python server.py --verbose   # Windows
```

The server will start on `http://localhost:8000`

**Note:** The `chmod` command is only needed on Mac/Linux to make scripts executable. Windows doesn't use this permission system.

### 5. Open Browser

Navigate to `http://localhost:8000` in your web browser.

## Using the Web Interface

### Installing Packages

1. Check boxes next to packages you want in the left sidebar
2. Click "Install Selected" in the main panel
3. Follow any permission prompts (sudo/admin)

### Updating Packages

1. Click "Update Packages"
2. Choose:
   - **Update All** - Update everything with available updates
   - **Select Updates Manually** - Choose specific packages
   - **No Updates** - Cancel

### Package Status Icons

- 💤 **Commented Out** - Package is disabled in packages.conf
- 📥 **Not Installed** - Package is available but not installed
- ✓ **Installed** - Package is currently installed
- 🔄 **Update Available** - A newer version is available

### Using the Command Console

Type commands in the console:

```
detect_os          # Show detected operating system
detect_pm          # Show package manager
list_packages      # List enabled packages
server_version     # Show server version
help               # Show available commands
```

### Using AI Assistant

1. Type a modification request in the AI text area
2. Click "Send to AI"
3. Review the generated code/suggestions
4. Use quick examples for common modifications

**Example Prompts:**
- "Add support for Snap packages on Linux"
- "Create a backup feature before updates"
- "Add installation progress percentage"
- "Add package search functionality"

See `CLAUDE_VIBES.md` for 50+ detailed examples.

## Command Line Usage

### Using setup.sh Directly

```bash
# Install all enabled packages
./setup.sh

# The script will:
# - Detect your OS and package manager
# - Install package manager if needed (macOS only)
# - Read packages.conf
# - Install all uncommented packages
```

## Project Structure

```
desktop/install/
├── README.md                 # This file - complete documentation
├── CLAUDE_VIBES.md          # AI modification examples for Claude Code CLI
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore rules
├── .env.example            # Example environment configuration
│
├── desktop.conf            # Package configuration (comment/uncomment packages)
├── setup.sh               # Cross-platform installation script (executable)
├── server.py              # Python backend server (executable)
├── index.html             # Complete web frontend (no external dependencies)
├── quickstart.sh          # Interactive setup wizard (optional, executable)
│
└── (External dependency)
    └── ../../docker/.env  # Environment variables (API keys) - optional
```

### Core Files

**setup.sh** - Bash script for command-line installation
- Detects OS and package manager automatically
- Reads packages.conf and installs enabled packages
- Handles sudo/admin permissions
- Cross-platform: macOS, Windows (Git Bash/WSL), Linux

**server.py** - Python HTTP server (v1.0.0)
- Package detection and management
- LLM integration for AI features
- Command execution interface
- RESTful API for frontend
- No external dependencies except optional `anthropic` package

**index.html** - Complete web interface
- Package management UI with narrow sidebar navigation
- Command console
- AI assistant interface
- Real-time status updates
- Modern design inspired by Claude.ai
- All CSS and JavaScript included inline (no external files)

**packages.conf** - Package configuration
- Use `##` for true comments
- Use `#` prefix to disable a package
- Add inline descriptions after package name
- Example:
  ```conf
  ## Comments start with double ##
  libreoffice # Office Suite
  # blender # 3D Graphics (commented out, won't install)
  ```

## Architecture

### Data Flow

```
User Interface (index.html)
    ↓
HTTP Request → server.py (API)
    ↓
PackageManager class
    ↓
setup.sh or direct package manager commands
    ↓
System package manager (brew/apt/winget/etc)
```

### Features

- **Cross-Platform**: Automatically detects OS and uses appropriate package manager
  - Mac: Homebrew
  - Windows: winget
  - Linux: apt, dnf, or flatpak
  
- **Modern Web Interface**: Clean UI inspired by Claude.ai with narrow sidebar navigation
- **Package Status**: Real-time detection of installed packages and versions
- **Selective Updates**: Approve all updates at once or select individually
- **AI Integration**: Built-in LLM interface for generating modifications
- **Command Console**: Send commands directly to the Python server

## Backend Choice: Python

Python was chosen because:
1. **Cross-platform**: Identical behavior on Mac, Windows, and Linux
2. **Built-in HTTP server**: No external dependencies required
3. **Subprocess management**: Can execute shell scripts and PowerShell with proper elevation
4. **JSON/API**: Easy to serve package status and handle updates
5. **Permission handling**: Can prompt for sudo/admin elevation when needed

## Key Technical Components

### 1. Package Detection Strategy
- **Mac**: `brew list`, `mdls` for app metadata
- **Windows**: `winget list`, registry queries, `Get-ItemProperty`
- **Linux**: `dpkg -l`, `rpm -qa`, `flatpak list`

### 2. Permission Elevation
- **Mac/Linux**: `sudo` prompts in terminal, web UI shows command
- **Windows**: Python detects admin status and generates elevated PowerShell scripts

### 3. Server API Endpoints

All endpoints accessible at `http://localhost:8000/api/`

- **GET /api/status** - Server status and configuration
  ```json
  {
    "version": "1.0.0",
    "os": "macos",
    "package_manager": "brew",
    "llm_available": true
  }
  ```

- **GET /api/packages** - List all packages with status
  ```json
  {
    "packages": [
      {
        "name": "libreoffice",
        "description": "Office Suite",
        "installed": true,
        "version": "7.6.2",
        "update_available": true,
        "new_version": "7.6.4"
      }
    ]
  }
  ```

- **POST /api/install** - Install selected packages
  ```json
  {
    "packages": ["libreoffice", "gimp"]
  }
  ```

- **POST /api/update** - Update packages
  ```json
  {
    "mode": "all"  // or "selected" with packages array, or "none"
  }
  ```

- **POST /api/refresh** - Force refresh package cache

- **POST /api/execute** - Execute whitelisted commands
  ```json
  {
    "command": "detect_os"
  }
  ```

- **POST /api/llm** - Send prompts to AI (requires API key)
  ```json
  {
    "prompt": "Add support for snap packages",
    "context": "current_code_here"
  }
  ```

### 4. Real-time Status

Polling-based status updates for install progress. Package information is cached for 30 seconds to improve performance.

## Troubleshooting

### Server Won't Start

**Port already in use:**
The server will automatically try ports 8000-8010. If all are in use:
```bash
python3 server.py --port 9000
```

**Python not found:**
- Ensure Python 3.6+ is installed
- Try `python` instead of `python3` on Windows
- Download from: https://www.python.org/downloads/

### Permission Errors

**macOS/Linux:**
```bash
# Run commands with sudo when prompted
sudo apt-get install package-name  # Linux
brew install package-name          # macOS (no sudo needed)
```

**Windows:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"
```

### Package Manager Not Found

**macOS:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Windows:**
- Install winget from Microsoft Store
- Or download from: https://github.com/microsoft/winget-cli/releases

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update

# Fedora
sudo dnf check-update

# Or install flatpak
sudo apt-get install flatpak  # Ubuntu/Debian
sudo dnf install flatpak      # Fedora
```

### Packages Not Detecting

1. Ensure package manager is properly installed
2. Try running with verbose logging:
   ```bash
   python3 server.py --verbose
   ```
3. Manually test package manager:
   ```bash
   brew list              # macOS
   apt list --installed   # Ubuntu/Debian
   winget list           # Windows
   ```

### LLM Not Available

1. Check that `.env` file exists at `../../docker/.env`
2. Verify API key is correct
3. Install anthropic package:
   ```bash
   pip install anthropic
   ```

### UI Issues

**Packages not loading:**
- Check browser console for errors (F12)
- Verify server is running
- Try refreshing the page

**Checkboxes disabled:**
- Wait for initial package detection to complete
- Commented packages (with 💤) cannot be selected

## Advanced Configuration

### Adding Custom Packages

Edit `packages.conf` and add package names:

```conf
## Custom additions
my-custom-package # My custom tool
another-package # Another tool
```

Package names should match your package manager's repository:
- **Homebrew**: Check https://formulae.brew.sh/
- **apt**: Check `apt search package-name`
- **winget**: Check `winget search package-name`

### Customizing the UI

All UI code is in `index.html` with inline CSS and JavaScript:
- Edit the `<style>` section for styling
- Edit the `<script>` section for functionality
- Color scheme variables in `:root` CSS

### Adding New Package Managers

Edit `server.py` in the `PackageManager` class:

```python
def detect_package_manager(self):
    """Add custom package manager detection"""
    if self.command_exists("my-package-manager"):
        return "my-pm"
    # ... rest of code
```

Then add installation and detection methods for the new package manager.

### Modifying Cache Duration

Edit `server.py` in the `PackageManager.__init__` method:

```python
self.cache_ttl = 60  # Cache for 60 seconds instead of 30
```

## Dependencies

### Required
- Python 3.6+ (included with most systems)
- Web browser (any modern browser)

### Optional
- `anthropic` Python package (for LLM features)
- Package manager: brew/winget/apt/dnf/flatpak (auto-detected)

## Platform Support

| Platform | Package Manager | Status |
|----------|----------------|--------|
| macOS 10.14+ | Homebrew | ✓ Fully Supported |
| Windows 10+ | winget | ✓ Fully Supported |
| Ubuntu 18.04+ | apt | ✓ Fully Supported |
| Debian 9+ | apt | ✓ Fully Supported |
| Fedora 30+ | dnf | ✓ Fully Supported |
| CentOS 7+ | yum | ✓ Fully Supported |
| Any Linux | flatpak | ✓ Fully Supported |

## Browser Compatibility

- Chrome/Edge: ✓ Full support
- Firefox: ✓ Full support
- Safari: ✓ Full support
- Opera: ✓ Full support
- Mobile browsers: ✓ Responsive design

## Security Considerations

### API Key Security
- Never commit `.env` file to version control
- Add `../../docker/.env` to `.gitignore`
- Keep API key private
- Rotate keys periodically

### Command Execution
The server only allows whitelisted commands:
- `detect_os`
- `detect_pm`
- `list_packages`
- `server_version`

To add more, edit the `safe_commands` dict in `server.py`.

### Package Installation
- Always review packages before installation
- Use official package repositories
- Keep package managers updated

## Files You Can Reuse

From the initial download, you should use these files **as-is**:

✅ **Reuse these files:**
- `LICENSE` - MIT License
- `CLAUDE_VIBES.md` - AI modification examples  
- `.env.example` - Environment template
- `.gitignore` - Git ignore rules
- `quickstart.sh` - Setup wizard

📝 **Use the updated versions:**
- `README.md` - **This file** (consolidated documentation)
- `packages.conf` - Updated to use `##` for comments
- `server.py` - Updated to parse new comment format
- `index.html` - Redesigned UI inspired by Claude.ai
- `setup.sh` - Same as original

❌ **Don't use these (now obsolete):**
- `SETUP.md` - Content merged into this README
- `PROJECT_STRUCTURE.md` - Content merged into this README

## License

MIT License - Feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- Use the built-in AI console
- File an issue on the repository
- See `CLAUDE_VIBES.md` for modification examples
