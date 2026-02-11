#!/usr/bin/env python3
"""
CLE-Net Build Script

This script helps build CLE-Net as a standalone executable for normal users.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = ['pyinstaller']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("Dependencies installed successfully!\n")
    else:
        print("All dependencies are installed!\n")


def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("Building CLE-Net executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build using PyInstaller
    try:
        subprocess.check_call([sys.executable, '-m', 'PyInstaller', 'cle_net.spec'])
        print("\nBuild completed successfully!")
        print(f"Executable location: {os.path.abspath('dist/cle-net.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)


def create_installer():
    """Create a simple installer script."""
    print("Creating installer script...")
    
    installer_script = """@echo off
echo CLE-Net Installer
echo ================
echo.
echo This will install CLE-Net to your system.
echo.
set /p install_dir="Enter installation directory (default: C:\\CLE-Net): "
if "%install_dir%"=="" set install_dir=C:\\CLE-Net

echo Creating directory: %install_dir%
mkdir "%install_dir%" 2>nul

echo Copying files...
copy "cle-net.exe" "%install_dir%\\" >nul
copy "README.md" "%install_dir%\\" >nul
copy "LICENSE" "%install_dir%\\" >nul

echo Creating data directory...
mkdir "%install_dir%\\data" 2>nul

echo.
echo Installation completed successfully!
echo.
echo CLE-Net has been installed to: %install_dir%
echo.
echo To run CLE-Net, navigate to the installation directory and run:
echo   cle-net.exe
echo.
pause
"""
    
    with open('install.bat', 'w') as f:
        f.write(installer_script)
    
    print("Installer script created: install.bat")


def create_user_guide():
    """Create a user guide for normal users."""
    print("Creating user guide...")
    
    user_guide = """# CLE-Net User Guide

## What is CLE-Net?

CLE-Net (Cognitive Logic Extraction Network) is a blockchain-based system that discovers and validates cognitive laws from AI-generated data and human interactions.

## Installation

### Option 1: Using the Executable (Recommended for Normal Users)

1. Download the CLE-Net executable from the releases page
2. Run the installer (install.bat) on Windows
3. Navigate to the installation directory
4. Run `cle-net.exe`

### Option 2: Using pip (Recommended for Developers)

```bash
pip install cle-net
```

## Getting Started

### Interactive Mode

Simply run CLE-Net without any arguments to start interactive mode:

```bash
cle-net
```

In interactive mode, you can:
- Type any text to process it and discover cognitive laws
- Type `help` to see available commands
- Type `status` to see current status
- Type `exit` to quit

### Processing Files

Process data from a text file:

```bash
cle-net --file data.txt
```

### Processing AI API Data

Process data from OpenAI:

```bash
cle-net --api openai --api-key YOUR_API_KEY --prompt "Analyze customer support interactions"
```

Process data from Anthropic:

```bash
cle-net --api anthropic --api-key YOUR_API_KEY --prompt "Analyze customer support interactions"
```

### Exporting Results

Export all discovered rules to a file:

```bash
cle-net --export results.json
```

## Understanding the Output

When you process data, CLE-Net will:

1. **Extract symbols** from the text
2. **Discover rules** using symbolic regression
3. **Create commits** for discovered rules
4. **Display results** showing:
   - Rule hash (unique identifier)
   - Confidence score (0.0 to 1.0)
   - Timestamp

## Example Usage

### Example 1: Interactive Mode

```
CLE-Net> Customers who contact support multiple times about the same issue are likely frustrated.
Processing data from interactive...
  Data length: 98 characters
  Generated 1 rule commits

Discovered Rules:
  1. Rule Hash: a1b2c3d4e5f6g7h8...
     Confidence: 0.85
     Timestamp: 2026-02-10 13:45:00

1 rule(s) discovered!
```

### Example 2: Processing a File

```bash
cle-net --file customer_interactions.txt
```

This will:
- Read the file
- Process the content
- Discover cognitive laws
- Save results to `customer_interactions_results.json`

### Example 3: Using AI API

```bash
cle-net --api openai --api-key sk-... --prompt "Generate 10 customer support scenarios"
```

This will:
- Send the prompt to OpenAI
- Get AI-generated data
- Process the AI response
- Discover cognitive laws
- Save results to `openai_results.json`

## Data Storage

CLE-Net stores data in the following locations:

- **Data directory**: `./data/` (or specified with `--data-path`)
- **Results files**: JSON files with discovered rules
- **Agent state**: Automatically saved and loaded

## Troubleshooting

### "CLE-Net package not found"

Install CLE-Net:
```bash
pip install cle-net
```

### "API library not installed"

Install the required AI library:
```bash
pip install openai  # for OpenAI
pip install anthropic  # for Anthropic
```

### "File not found"

Make sure the file path is correct and the file exists.

## Advanced Usage

### Custom Data Path

```bash
cle-net --data-path /path/to/data
```

### Combining Options

```bash
cle-net --file data.txt --export results.json
```

## Support

For more information, visit:
- GitHub: https://github.com/Abdelrahman-sadek/CLE-Net
- Documentation: https://github.com/Abdelrahman-sadek/CLE-Net/blob/main/README.md
- Issues: https://github.com/Abdelrahman-sadek/CLE-Net/issues
"""
    
    with open('USER_GUIDE.md', 'w') as f:
        f.write(user_guide)
    
    print("User guide created: USER_GUIDE.md")


def main():
    """Main build function."""
    print("=" * 70)
    print("CLE-Net Build Script")
    print("=" * 70)
    print()
    
    # Check dependencies
    check_dependencies()
    
    # Build executable
    build_executable()
    
    # Create installer
    create_installer()
    
    # Create user guide
    create_user_guide()
    
    print("\n" + "=" * 70)
    print("Build completed successfully!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Test the executable: dist\\cle-net.exe")
    print("  2. Run the installer: install.bat")
    print("  3. Read the user guide: USER_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
