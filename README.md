# RAWG MCP Server

This is a JSON-RPC MCP server for accessing the RAWG Video Games Database. It allows you to search games, fetch popular titles, filter by genre or platform, get detailed game info, DLCs, and stores.

## Features / Available Tools

The MCP exposes the following tools:

- rawg_search – Search games by name.
- rawg_popular – Fetch a list of popular games.
- rawg_by_genre – Search games filtered by genre (e.g., action, RPG, strategy).
- rawg_by_platform – Search games filtered by platform (PC, PlayStation, Xbox, Switch).
- rawg_game_details – Get detailed information about a specific game.
- rawg_game_stores – Retrieve stores where a specific game can be purchased.
- rawg_game_dlcs – Retrieve DLCs or expansions for a specific game.

## Requirements

The server requires Python 3.10+. Required packages:

- fastapi==0.109.1
- uvicorn==0.23.2
- requests==2.32.0
- python-dotenv==1.0.1
- jsonrpcserver==6.8.1

## Setup

1. Clone the repository:

```
git clone https://github.com/yourusername/rawg-mcp-server.git
cd rawg-mcp-server
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Get a RAWG API key (free) from https://api.rawg.io

4. Create a .env file in the project root with your key:

```
RAWG_API_KEY=your_rawg_api_key_here
```

5. Start the server:

```
python rawg_mcp_server.py
```

The server will run on http://localhost:8003.

## Endpoints

- JSON-RPC endpoint: / – Handles all tool calls.
- Health check: /health – Returns server status.
- Info: /info – Returns server name, version, description, and available methods.

## Usage Example

Using curl to search for games called Hollow Knight:

```
curl -X POST http://localhost:8003/ -H "Content-Type: application/json" -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "rawg_search",
    "params": {"query": "Hollow Knight", "page_size": 5}
}'
```
