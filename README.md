# Sales MCP Server

A Model Context Protocol (MCP) server that exposes sales data tools for querying customer sales from a CSV file.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Claude Code](https://claude.ai/code)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/chuvanan/a-mcp-server.git
cd a-mcp-server
```

2. Install dependencies:

```bash
uv sync
```

## Connecting to Claude Code

Add the server to Claude Code by running this command from the project directory:

```bash
claude mcp add sales-mcp-server -- uv run main.py
```

Or manually add it to your `.mcp.json`:

```json
{
  "mcpServers": {
    "sales-mcp-server": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "/absolute/path/to/a-mcp-server"
    }
  }
}
```

Verify the server is connected:

```bash
claude mcp list
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_all_customers` | Returns a sorted list of all unique customer names |
| `get_sales_from_customer(customer_name)` | Returns a list of individual sale amounts for a customer |
| `get_total_spent_by_customer(customer_name)` | Returns the total amount spent by a customer |
| `get_total_sales` | Returns the combined total spent by all customers |

## Example Usage

Once connected, ask Claude Code questions like:

- "How many customers are there?"
- "What are the total sales for Alice?"
- "Get all sales by Bob"
- "What is the total revenue across all customers?"
