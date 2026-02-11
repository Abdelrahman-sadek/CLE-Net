# CLE-Net User Guide

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
