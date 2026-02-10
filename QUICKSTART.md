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
