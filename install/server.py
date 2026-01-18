#!/usr/bin/env python3
"""
Cross-Platform Package Manager Server
Provides web API for managing software installations
"""

import os
import sys
import json
import subprocess
import threading
import time
import platform
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import socket

VERSION = "1.0.0"
DEFAULT_PORT = 8000

class PackageManager:
    """Handles package detection and management across platforms"""
    
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.packages_file = self.base_dir / "desktop.conf"
        self.os_type = self.detect_os()
        self.pkg_manager = self.detect_package_manager()
        self.cache = {}
        self.cache_time = 0
        self.cache_ttl = 300  # Cache for 5 minutes instead of 30 seconds
        
    def detect_os(self):
        """Detect operating system"""
        system = platform.system()
        if system == "Darwin":
            return "macos"
        elif system == "Linux":
            return "linux"
        elif system == "Windows":
            return "windows"
        else:
            return "unknown"
    
    def detect_package_manager(self):
        """Detect available package manager"""
        if self.os_type == "macos":
            if self.command_exists("brew"):
                return "brew"
        elif self.os_type == "linux":
            if self.command_exists("apt-get"):
                return "apt"
            elif self.command_exists("dnf"):
                return "dnf"
            elif self.command_exists("yum"):
                return "yum"
            elif self.command_exists("flatpak"):
                return "flatpak"
        elif self.os_type == "windows":
            if self.command_exists("winget"):
                return "winget"
        return "none"
    
    def command_exists(self, command):
        """Check if command exists in PATH"""
        try:
            if self.os_type == "windows":
                subprocess.run(["where", command], 
                             capture_output=True, check=True)
            else:
                subprocess.run(["which", command], 
                             capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def read_packages(self):
        """Read packages from config file"""
        packages = []
        all_packages = []
        
        try:
            with open(self.packages_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip lines starting with ##
                    if line.startswith('##'):
                        continue
                    
                    is_commented = line.startswith('#')
                    
                    # Remove leading # if present
                    if is_commented:
                        line = line[1:].strip()
                    
                    # Split on # to separate package name from description
                    parts = line.split('#', 1)
                    package_name = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ''
                    
                    if package_name:
                        all_packages.append({
                            'name': package_name,
                            'enabled': not is_commented,
                            'description': description
                        })
                        if not is_commented:
                            packages.append(package_name)
        except FileNotFoundError:
            pass
        
        return packages, all_packages
    
    def is_installed(self, package):
        """Check if package is installed"""
        try:
            if self.pkg_manager == "brew":
                result = subprocess.run(
                    ["brew", "list", "--cask", package],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        ["brew", "list", package],
                        capture_output=True, text=True
                    )
                return result.returncode == 0
                
            elif self.pkg_manager == "apt":
                result = subprocess.run(
                    ["dpkg", "-l", package],
                    capture_output=True, text=True
                )
                return "ii" in result.stdout
                
            elif self.pkg_manager in ["dnf", "yum"]:
                result = subprocess.run(
                    ["rpm", "-qa", package],
                    capture_output=True, text=True
                )
                return package in result.stdout
                
            elif self.pkg_manager == "flatpak":
                result = subprocess.run(
                    ["flatpak", "list"],
                    capture_output=True, text=True
                )
                return package in result.stdout
                
            elif self.pkg_manager == "winget":
                result = subprocess.run(
                    ["winget", "list", package],
                    capture_output=True, text=True
                )
                return package.lower() in result.stdout.lower()
                
        except Exception as e:
            print(f"Error checking if {package} is installed: {e}")
        
        return False
    
    def get_version(self, package):
        """Get installed version of package"""
        try:
            if self.pkg_manager == "brew":
                result = subprocess.run(
                    ["brew", "info", "--cask", package],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        ["brew", "info", package],
                        capture_output=True, text=True
                    )
                
                # Extract version from brew info output
                match = re.search(r'(\d+\.\d+(?:\.\d+)?)', result.stdout)
                if match:
                    return match.group(1)
                    
            elif self.pkg_manager == "apt":
                result = subprocess.run(
                    ["dpkg", "-l", package],
                    capture_output=True, text=True
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith("ii"):
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
                            
            elif self.pkg_manager in ["dnf", "yum"]:
                result = subprocess.run(
                    ["rpm", "-q", package],
                    capture_output=True, text=True
                )
                # Extract version from rpm output
                match = re.search(r'-(\d+\.\d+(?:\.\d+)?)', result.stdout)
                if match:
                    return match.group(1)
                    
            elif self.pkg_manager == "winget":
                result = subprocess.run(
                    ["winget", "list", package],
                    capture_output=True, text=True
                )
                # Parse winget output for version
                lines = result.stdout.split('\n')
                for line in lines:
                    if package.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1]
                            
        except Exception as e:
            print(f"Error getting version for {package}: {e}")
        
        return "unknown"
    
    def get_update_info(self, package):
        """Check if update is available"""
        try:
            if self.pkg_manager == "brew":
                result = subprocess.run(
                    ["brew", "outdated", "--cask", package],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        ["brew", "outdated", package],
                        capture_output=True, text=True
                    )
                
                if package in result.stdout:
                    # Extract new version
                    match = re.search(r'(\d+\.\d+(?:\.\d+)?)\s*<\s*(\d+\.\d+(?:\.\d+)?)', 
                                    result.stdout)
                    if match:
                        return {
                            'available': True,
                            'new_version': match.group(2)
                        }
                        
            elif self.pkg_manager == "apt":
                result = subprocess.run(
                    ["apt", "list", "--upgradable", package],
                    capture_output=True, text=True
                )
                if package in result.stdout:
                    match = re.search(r'\[upgradable from: ([\d.]+)\]', result.stdout)
                    if match:
                        return {
                            'available': True,
                            'new_version': 'available'
                        }
                        
        except Exception as e:
            print(f"Error checking updates for {package}: {e}")
        
        return {
            'available': False,
            'new_version': None
        }
    
    def get_package_status(self, package_name, description=''):
        """Get complete status for a package"""
        installed = self.is_installed(package_name)
        version = None
        update_info = {'available': False, 'new_version': None}
        
        if installed:
            version = self.get_version(package_name)
            update_info = self.get_update_info(package_name)
        
        return {
            'name': package_name,
            'description': description,
            'installed': installed,
            'version': version,
            'update_available': update_info['available'],
            'new_version': update_info['new_version']
        }
    
    def get_all_packages_status(self, force_refresh=False):
        """Get status for all packages with caching"""
        current_time = time.time()
        
        if not force_refresh and (current_time - self.cache_time) < self.cache_ttl:
            if 'packages' in self.cache:
                return self.cache['packages']
        
        enabled_packages, all_packages = self.read_packages()
        packages_status = []
        
        for pkg_info in all_packages:
            status = self.get_package_status(pkg_info['name'], pkg_info.get('description', ''))
            status['enabled'] = pkg_info['enabled']
            packages_status.append(status)
        
        self.cache['packages'] = packages_status
        self.cache_time = current_time
        
        return packages_status
    
    def install_package(self, package):
        """Install a package"""
        try:
            if self.pkg_manager == "brew":
                # Try cask first, fall back to formula
                result = subprocess.run(
                    ["brew", "install", "--cask", package],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        ["brew", "install", package],
                        capture_output=True, text=True, check=True
                    )
                return True
                
            elif self.pkg_manager == "apt":
                result = subprocess.run(
                    ["sudo", "apt-get", "install", "-y", package],
                    capture_output=True, text=True, check=True
                )
                return True
                
            elif self.pkg_manager == "dnf":
                result = subprocess.run(
                    ["sudo", "dnf", "install", "-y", package],
                    capture_output=True, text=True, check=True
                )
                return True
                
            elif self.pkg_manager == "winget":
                result = subprocess.run(
                    ["winget", "install", "-e", "--id", package],
                    capture_output=True, text=True, check=True
                )
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            return False
        
        return False
    
    def update_package(self, package):
        """Update a package"""
        try:
            if self.pkg_manager == "brew":
                subprocess.run(
                    ["brew", "upgrade", "--cask", package],
                    capture_output=True, text=True
                )
                subprocess.run(
                    ["brew", "upgrade", package],
                    capture_output=True, text=True
                )
                return True
                
            elif self.pkg_manager == "apt":
                subprocess.run(
                    ["sudo", "apt-get", "install", "--only-upgrade", "-y", package],
                    capture_output=True, text=True, check=True
                )
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"Error updating {package}: {e}")
            return False
        
        return False


class LLMIntegration:
    """Handle LLM API integration"""
    
    def __init__(self):
        self.api_key = self.load_api_key()
    
    def load_api_key(self):
        """Load API key from .env file two levels up"""
        env_path = Path(__file__).parent.parent.parent / "docker" / ".env"
        
        if not env_path.exists():
            return None
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('ANTHROPIC_API_KEY='):
                        return line.split('=', 1)[1].strip().strip('"\'')
        except Exception as e:
            print(f"Error loading API key: {e}")
        
        return None
    
    def send_prompt(self, prompt, context=""):
        """Send prompt to LLM API"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'No API key found in ../../docker/.env'
            }
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = f"{prompt}\n\nContext:\n{context}" if context else prompt
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            
            return {
                'success': True,
                'response': response.content[0].text
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'anthropic package not installed. Run: pip install anthropic'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class APIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for API endpoints"""
    
    package_manager = None
    llm = None
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_file('index.html')
        elif parsed_path.path == '/api/status':
            self.handle_status()
        elif parsed_path.path == '/api/packages':
            self.handle_packages()
        elif parsed_path.path.startswith('/api/'):
            self.send_json_response({'error': 'Not found'}, 404)
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json_response({'error': 'Invalid JSON'}, 400)
            return
        
        if parsed_path.path == '/api/install':
            self.handle_install(data)
        elif parsed_path.path == '/api/update':
            self.handle_update(data)
        elif parsed_path.path == '/api/execute':
            self.handle_execute(data)
        elif parsed_path.path == '/api/llm':
            self.handle_llm(data)
        elif parsed_path.path == '/api/refresh':
            self.handle_refresh()
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def handle_status(self):
        """Return server status"""
        self.send_json_response({
            'version': VERSION,
            'os': self.package_manager.os_type,
            'package_manager': self.package_manager.pkg_manager,
            'llm_available': self.llm.api_key is not None
        })
    
    def handle_packages(self):
        """Return package status"""
        packages = self.package_manager.get_all_packages_status()
        self.send_json_response({
            'packages': packages,
            'os': self.package_manager.os_type,
            'package_manager': self.package_manager.pkg_manager
        })
    
    def handle_refresh(self):
        """Force refresh package cache only if needed"""
        # Check if cache is recent (less than 10 seconds old)
        current_time = time.time()
        cache_age = current_time - self.package_manager.cache_time
        
        if cache_age < 10:
            # Cache is fresh, return it immediately
            packages = self.package_manager.get_all_packages_status(force_refresh=False)
            self.send_json_response({
                'success': True,
                'packages': packages,
                'cached': True,
                'cache_age': round(cache_age, 2)
            })
        else:
            # Cache is stale, refresh it
            packages = self.package_manager.get_all_packages_status(force_refresh=True)
            self.send_json_response({
                'success': True,
                'packages': packages,
                'cached': False
            })
    
    def handle_install(self, data):
        """Handle package installation"""
        packages = data.get('packages', [])
        
        if not packages:
            self.send_json_response({'error': 'No packages specified'}, 400)
            return
        
        results = {}
        for package in packages:
            results[package] = self.package_manager.install_package(package)
        
        self.send_json_response({
            'success': True,
            'results': results
        })
    
    def handle_update(self, data):
        """Handle package updates"""
        mode = data.get('mode', 'none')
        packages = data.get('packages', [])
        
        if mode == 'none':
            self.send_json_response({'success': True, 'message': 'No updates performed'})
            return
        
        if mode == 'all':
            all_packages = self.package_manager.get_all_packages_status()
            packages = [p['name'] for p in all_packages if p['update_available']]
        
        results = {}
        for package in packages:
            results[package] = self.package_manager.update_package(package)
        
        self.send_json_response({
            'success': True,
            'results': results
        })
    
    def handle_execute(self, data):
        """Handle command execution"""
        command = data.get('command', '')
        
        if not command:
            self.send_json_response({'error': 'No command specified'}, 400)
            return
        
        # Safe command whitelist
        safe_commands = {
            'detect_os': lambda: {'os': self.package_manager.os_type},
            'detect_pm': lambda: {'package_manager': self.package_manager.pkg_manager},
            'list_packages': lambda: {'packages': self.package_manager.read_packages()[0]},
            'server_version': lambda: {'version': VERSION},
        }
        
        if command in safe_commands:
            result = safe_commands[command]()
            self.send_json_response({'success': True, 'result': result})
        else:
            self.send_json_response({'error': 'Unknown or unsafe command'}, 400)
    
    def handle_llm(self, data):
        """Handle LLM prompts"""
        prompt = data.get('prompt', '')
        context = data.get('context', '')
        
        if not prompt:
            self.send_json_response({'error': 'No prompt provided'}, 400)
            return
        
        result = self.llm.send_prompt(prompt, context)
        self.send_json_response(result)
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_file(self, filename):
        """Serve a static file"""
        try:
            file_path = Path(__file__).parent / filename
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            if filename.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif filename.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif filename.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"File not found: {filename}")
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def is_port_in_use(port):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def main():
    """Main server function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cross-Platform Package Manager Server')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, 
                       help=f'Port to run server on (default: {DEFAULT_PORT})')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    args = parser.parse_args()
    
    # Initialize package manager
    base_dir = Path(__file__).parent
    pkg_mgr = PackageManager(base_dir)
    llm = LLMIntegration()
    
    # Set class variables
    APIHandler.package_manager = pkg_mgr
    APIHandler.llm = llm
    
    # Find available port
    port = args.port
    while is_port_in_use(port) and port < args.port + 10:
        port += 1
    
    if port != args.port:
        print(f"Port {args.port} is in use, using port {port} instead")
    
    # Start server
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print(f"╔═══════════════════════════════════════════════════════════╗")
    print(f"║   Cross-Platform Package Manager Server v{VERSION}       ║")
    print(f"╠═══════════════════════════════════════════════════════════╣")
    print(f"║   Server running at: http://localhost:{port}              ║")
    print(f"║   OS: {pkg_mgr.os_type.ljust(48)} ║")
    print(f"║   Package Manager: {pkg_mgr.pkg_manager.ljust(38)} ║")
    print(f"║   LLM Available: {'Yes' if llm.api_key else 'No'.ljust(42)} ║")
    print(f"╚═══════════════════════════════════════════════════════════╝")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()
        print("Server stopped.")


if __name__ == '__main__':
    main()
