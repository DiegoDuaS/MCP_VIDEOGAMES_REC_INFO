# RAWG Gaming MCP Server

A Model Context Protocol (MCP) server that provides gaming information and recommendations using the RAWG Video Games Database API.

## Features

- **Game Search**: Find games by name with detailed information
- **Popular Games**: Get lists of currently popular games
- **Genre Filtering**: Browse games by specific genres (action, RPG, strategy, etc.)
- **Platform Filtering**: Find games available on specific platforms
- **Detailed Game Info**: Get comprehensive details about any game including developers, publishers, ratings, and descriptions
- **Trending Games**: Discover what's currently trending in gaming
- **Smart Logging**: All interactions are logged for debugging and analysis

## Setup Instructions

### 1. Install Dependencies

Make sure you have Python 3.8+ installed, then install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Get a RAWG API Key

1. Visit [https://rawg.io/apidocs](https://rawg.io/apidocs)
2. Click "Get API Key" 
3. Create a free account if you don't have one
4. Once logged in, you'll see your API key in the dashboard
5. Copy your API key (it looks like: `1234567890abcdef1234567890abcdef12345678`)

### 3. Create Environment File

Create a `.env` file in the same directory as the server script:

```bash
# .env file
RAWG_API_KEY=your_actual_api_key_here
```

Replace `your_actual_api_key_here` with the API key you copied from RAWG.

### 4. Test the Server

Run the server to make sure everything is working:

```bash
python mcp_server.py
```

If successful, you should see the server start without errors.

## Available Tools

### `search_games(query, page_size=5)`
Search for games by name.
- `query`: Game name to search for
- `page_size`: Number of results (1-20, default 5)

**Example**: Search for "witcher" games

### `get_popular_games(page_size=10)`
Get a list of popular games.
- `page_size`: Number of games to return (1-20, default 10)

### `get_games_by_genre(genre, page_size=10)`
Find games in a specific genre.
- `genre`: Genre name (action, rpg, strategy, adventure, shooter, etc.)
- `page_size`: Number of games to return (1-20, default 10)

**Example**: Get top RPG games

### `get_games_by_platform(platform, page_size=10)`
Find games for a specific platform.
- `platform`: Platform name (pc, playstation-5, xbox-series-x, nintendo-switch, etc.)
- `page_size`: Number of games to return (1-20, default 10)

**Example**: Get games for Nintendo Switch

### `get_game_details(game_name)`
Get detailed information about a specific game.
- `game_name`: Exact or partial game name

**Example**: Get details about "Cyberpunk 2077"

### `get_trending_games(page_size=10)`
Get currently trending games.
- `page_size`: Number of games to return (1-20, default 10)

## Usage Examples

### With MCP Client
```python
# Search for games
search_games("minecraft")

# Get popular RPG games
get_games_by_genre("rpg", 5)

# Get detailed info about a specific game
get_game_details("The Legend of Zelda: Breath of the Wild")

# Find games for PlayStation 5
get_games_by_platform("playstation-5", 8)
```

## File Structure

```
rawg-gaming-server/
├── mcp_server.py          # Main server file
├── requirements.txt       # Python dependencies
├── .env                  # API key configuration (create this)
├── README.md             # This file
└── logs/
    └── rawg_mcp_log.json # Interaction logs (auto-created)
```

## Rate Limiting

The server implements basic rate limiting to be respectful to the RAWG API:
- 1 request per second maximum
- Automatic retry handling for failed requests
- Timeout handling (10 second timeout per request)

## Logging

All interactions are logged to `logs/rawg_mcp_log.json` including:
- User requests
- API responses
- Error messages
- Timestamps

This helps with debugging and understanding usage patterns.

## Common Issues

### "RAWG_API_KEY not configured" error
- Make sure your `.env` file exists in the correct directory
- Verify your API key is correct and active
- Check that the `.env` file has no extra spaces or quotes around the key

### "Rate limit exceeded" errors
- The free RAWG API has rate limits
- The server includes built-in rate limiting to prevent this
- If you hit limits, wait a few minutes before making more requests

### Games not found
- RAWG database may not have every game
- Try different search terms or partial names
- Some very new or very old games might not be indexed

## API Credits

This server uses the [RAWG Video Games Database API](https://rawg.io/apidocs). 

- Free tier: 20,000 requests per month
- No commercial use restrictions for personal projects
- Attribution appreciated but not required

## License

This MCP server is provided as-is for educational and personal use. Please respect RAWG's API terms of service and rate limits.

## Support

For issues with this MCP server, check:
1. Your `.env` file configuration
2. Internet connection
3. RAWG API status at [https://rawg.io](https://rawg.io)

The server logs all interactions to help with debugging - check the logs folder for detailed error information.