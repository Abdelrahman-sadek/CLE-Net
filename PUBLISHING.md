# Publishing CLE-Net for Normal Users

This guide provides comprehensive instructions on how to publish CLE-Net to make it accessible and usable by normal users.

## Table of Contents

1. [PyPI Publishing](#pypi-publishing)
2. [Docker Publishing](#docker-publishing)
3. [Documentation Website](#documentation-website)
4. [Quick Start Guide](#quick-start-guide)
5. [Distribution Options](#distribution-options)

---

## PyPI Publishing

Publishing to PyPI allows users to install CLE-Net using `pip install cle-net`.

### Prerequisites

```bash
# Install build tools
pip install build twine setuptools wheel

# Install PyPI credentials
pip install keyring
```

### Step 1: Create `pyproject.toml`

Create a `pyproject.toml` file in the project root:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "cle-net"
version = "0.1.0"
description = "Cognitive Logic Extraction Network - A blockchain for cognitive law discovery"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Abdelrahman Sadek", email = "your.email@example.com"}
]
keywords = ["blockchain", "cognitive", "cosmos-sdk", "tendermint"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

dependencies = [
    "dataclasses-json>=0.5.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.990",
]

[project.urls]
Homepage = "https://github.com/Abdelrahman-sadek/CLE-Net"
Documentation = "https://cle-net.readthedocs.io"
Repository = "https://github.com/Abdelrahman-sadek/CLE-Net.git"
Issues = "https://github.com/Abdelrahman-sadek/CLE-Net/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["core*"]

[tool.setuptools.package-data]
"core" = ["*.py", "*.md"]
```

### Step 2: Create `MANIFEST.in`

Create a `MANIFEST.in` file to include non-Python files:

```text
include README.md
include LICENSE
include requirements.txt
recursive-include core *.py
recursive-include docs *.md
recursive-include examples *.py
```

### Step 3: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

### Step 4: Test the Package

```bash
# Install the package locally
pip install dist/cle-net-0.1.0-py3-none-any.whl

# Test import
python -c "from core.cosmos.app.app import CLENetApp; print('Import successful!')"
```

### Step 5: Publish to TestPyPI (Recommended First)

```bash
# Create TestPyPI account at https://test.pypi.org/account/register/

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ cle-net
```

### Step 6: Publish to PyPI

```bash
# Create PyPI account at https://pypi.org/account/register/

# Upload to PyPI
twine upload dist/*

# Users can now install with:
pip install cle-net
```

---

## Docker Publishing

Docker makes it easy for users to run CLE-Net without installing dependencies.

### Step 1: Create `Dockerfile`

Create a `Dockerfile` in the project root:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install CLE-Net
RUN pip install -e .

# Expose ports (if running a node)
EXPOSE 26656 26657 1317

# Set environment variables
ENV PYTHONPATH=/app
ENV CLE_NET_HOME=/data

# Create data directory
RUN mkdir -p /data

# Default command
CMD ["python", "-m", "core.cosmos.app.app"]
```

### Step 2: Create `docker-compose.yml`

Create a `docker-compose.yml` for easy deployment:

```yaml
version: '3.8'

services:
  cle-net-node:
    build: .
    container_name: cle-net-node
    ports:
      - "26656:26656"  # P2P
      - "26657:26657"  # RPC
      - "1317:1317"    # REST API
    volumes:
      - ./data:/data
      - ./config:/config
    environment:
      - CLE_NET_CHAIN_ID=cle-net-1
      - CLE_NET_MODE=testnet
    restart: unless-stopped
    command: python scripts/start_testnet.py

  cle-net-explorer:
    image: node:18-alpine
    container_name: cle-net-explorer
    ports:
      - "3000:3000"
    volumes:
      - ./explorer:/app
    working_dir: /app
    command: sh -c "npm install && npm start"
    depends_on:
      - cle-net-node
```

### Step 3: Build and Push Docker Image

```bash
# Build the image
docker build -t abdelrahmansadek/cle-net:latest .

# Test locally
docker run -p 26656:26656 -p 26657:26657 abdelrahmansadek/cle-net:latest

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push abdelrahmansadek/cle-net:latest

# Tag and push version
docker tag abdelrahmansadek/cle-net:latest abdelrahmansadek/cle-net:0.1.0
docker push abdelrahmansadek/cle-net:0.1.0
```

### Step 4: User Installation

Users can now run CLE-Net with:

```bash
# Pull the image
docker pull abdelrahmansadek/cle-net:latest

# Run a node
docker run -d \
  --name cle-net-node \
  -p 26656:26656 \
  -p 26657:26657 \
  -v $(pwd)/data:/data \
  abdelrahmansadek/cle-net:latest

# Or use docker-compose
docker-compose up -d
```

---

## Documentation Website

Create a professional documentation website using Read the Docs.

### Step 1: Create `docs/conf.py`

```python
# Configuration file for the Sphinx documentation builder.
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath('..'))

project = 'CLE-Net'
copyright = '2024, Abdelrahman Sadek'
author = 'Abdelrahman Sadek'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Auto-documentation
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
```

### Step 2: Create `docs/index.rst`

```rst
Welcome to CLE-Net Documentation
================================

CLE-Net (Cognitive Logic Extraction Network) is a blockchain platform for discovering and validating cognitive laws from human interaction.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   installation
   api
   architecture
   contributing

Quick Start
-----------

Install CLE-Net:

.. code-block:: bash

   pip install cle-net

Initialize a new node:

.. code-block:: python

   from core.cosmos.app.app import CLENetApp, AppConfig
   
   config = AppConfig(chain_id="cle-net-1")
   app = CLENetApp(config)
   app.init_chain({})

API Reference
------------

Core Modules
~~~~~~~~~~~~

.. automodule:: core.cosmos.app.app
   :members:

.. automodule:: core.cosmos.state_machine
   :members:

.. automodule:: core.cosmos.tendermint
   :members:
```

### Step 3: Build Documentation Locally

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### Step 4: Publish to Read the Docs

1. Go to https://readthedocs.org/
2. Click "Import a Project"
3. Connect your GitHub account
4. Select the CLE-Net repository
5. Configure settings:
   - Project slug: `cle-net`
   - Programming language: Python
   - Project homepage: https://github.com/Abdelrahman-sadek/CLE-Net
6. Click "Create"
7. Configure build settings:
   - OS: Ubuntu 22.04
   - Python version: 3.11
   - Build documentation: Yes
8. Click "Save"

Your documentation will be available at: https://cle-net.readthedocs.io

---

## Quick Start Guide

Create a user-friendly `QUICKSTART.md` file:

```markdown
# CLE-Net Quick Start Guide

Get started with CLE-Net in 5 minutes!

## Installation

### Option 1: Using pip (Recommended)

```bash
pip install cle-net
```

### Option 2: Using Docker

```bash
docker pull abdelrahmansadek/cle-net:latest
```

### Option 3: From Source

```bash
git clone https://github.com/Abdelrahman-sadek/CLE-Net.git
cd CLE-Net
pip install -r requirements.txt
pip install -e .
```

## Your First CLE-Net Application

Create a file `my_first_app.py`:

```python
from core.cosmos.app.app import CLENetApp, AppConfig, Message

# Create configuration
config = AppConfig(
    chain_id="my-cle-net-1",
    min_gas_prices="0.025ucle",
    block_time=5.0
)

# Initialize the app
app = CLENetApp(config)

# Initialize the chain
genesis_state = {
    "accounts": [],
    "validators": [],
    "app_state": {}
}
app.init_chain(genesis_state)

# Create and deliver a message
message = Message(
    type="test_message",
    sender="user1",
    data={"hello": "world"}
)

result = app.deliver_tx(message)
print(f"Message delivered: {result}")

# Begin a block
block_header = {
    "height": 1,
    "hash": "block_hash_1",
    "proposer": "user1",
    "timestamp": "2024-01-01T00:00:00Z"
}
app.begin_block(block_header)

# End and commit the block
app.end_block()
app.commit()

print("Block committed successfully!")
```

Run your application:

```bash
python my_first_app.py
```

## Running a Testnet Node

### Using Docker

```bash
docker run -d \
  --name cle-net-testnet \
  -p 26656:26656 \
  -p 26657:26657 \
  -v $(pwd)/data:/data \
  abdelrahmansadek/cle-net:latest \
  python scripts/start_testnet.py
```

### Using Python

```bash
python scripts/start_testnet.py
```

## Next Steps

- Read the [full documentation](https://cle-net.readthedocs.io)
- Explore the [API reference](https://cle-net.readthedocs.io/en/latest/api.html)
- Join our [community](https://github.com/Abdelrahman-sadek/CLE-Net/discussions)
- Check out [examples](https://github.com/Abdelrahman-sadek/CLE-Net/tree/main/examples)

## Getting Help

- 📖 [Documentation](https://cle-net.readthedocs.io)
- 💬 [Discussions](https://github.com/Abdelrahman-sadek/CLE-Net/discussions)
- 🐛 [Issues](https://github.com/Abdelrahman-sadek/CLE-Net/issues)
- 📧 Email: your.email@example.com
```

---

## Distribution Options

### 1. PyPI (Python Package Index)

**Best for:** Python developers

**Pros:**
- Easy installation with pip
- Automatic dependency management
- Version control
- Wide reach

**Cons:**
- Python-only
- Requires Python environment

**Installation:**
```bash
pip install cle-net
```

### 2. Docker Hub

**Best for:** System administrators and DevOps

**Pros:**
- Platform-independent
- Easy deployment
- Isolated environment
- Scalable

**Cons:**
- Larger download size
- Requires Docker

**Installation:**
```bash
docker pull abdelrahmansadek/cle-net:latest
```

### 3. GitHub Releases

**Best for:** Advanced users and contributors

**Pros:**
- Direct access to source code
- Version control
- Easy to fork and modify

**Cons:**
- Manual installation
- Requires build tools

**Installation:**
```bash
wget https://github.com/Abdelrahman-sadek/CLE-Net/releases/download/v0.1.0/cle-net-0.1.0.tar.gz
tar -xzf cle-net-0.1.0.tar.gz
cd cle-net-0.1.0
pip install -r requirements.txt
pip install -e .
```

### 4. Snap Store

**Best for:** Linux users

**Pros:**
- Universal Linux package
- Automatic updates
- Sandboxed

**Cons:**
- Linux only
- Requires snapd

**Installation:**
```bash
snap install cle-net
```

### 5. Homebrew (macOS)

**Best for:** macOS users

**Pros:**
- Native macOS package
- Easy installation
- Dependency management

**Cons:**
- macOS only

**Installation:**
```bash
brew tap abdelrahmansadek/cle-net
brew install cle-net
```

---

## Release Checklist

Before publishing a new release:

- [ ] Update version number in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run all tests: `python scripts/run_tests.py`
- [ ] Build documentation: `cd docs && make html`
- [ ] Create git tag: `git tag v0.1.0`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Build PyPI package: `python -m build`
- [ ] Upload to TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Test TestPyPI installation
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Build Docker image: `docker build -t abdelrahmansadek/cle-net:0.1.0 .`
- [ ] Push Docker image: `docker push abdelrahmansadek/cle-net:0.1.0`
- [ ] Create GitHub release
- [ ] Update documentation website
- [ ] Announce on social media

---

## Maintenance

### Regular Tasks

**Weekly:**
- Monitor GitHub issues and PRs
- Check test results
- Review community discussions

**Monthly:**
- Update dependencies
- Security audit
- Performance testing

**Quarterly:**
- Major version release
- Documentation review
- Community survey

### Security

- Regular dependency updates: `pip list --outdated`
- Security scanning: `pip-audit`
- Code review: `bandit -r core/`

---

## Support

For users needing help:

1. **Documentation:** https://cle-net.readthedocs.io
2. **Issues:** https://github.com/Abdelrahman-sadek/CLE-Net/issues
3. **Discussions:** https://github.com/Abdelrahman-sadek/CLE-Net/discussions
4. **Email:** your.email@example.com

---

## License

CLE-Net is released under the MIT License. See [LICENSE](LICENSE) for details.
