import os
import json
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from jsonrpcserver import method, async_dispatch as dispatch, Success, Error

# ======================
# Load environment variables
# ======================
load_dotenv()
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
if not RAWG_API_KEY:
    raise ValueError("Please set RAWG_API_KEY in your .env file")

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "rawg_mcp_log.json")
os.makedirs(LOG_DIR, exist_ok=True)

# Conversation log
rawg_conversation = []

# ======================
# FastAPI
# ======================
app = FastAPI(title="RAWG MCP JSON-RPC Server")

# ======================
# Logging
# ======================
def save_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(rawg_conversation, f, indent=2, ensure_ascii=False)

def log_message(role, content):
    rawg_conversation.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
    save_log()

# ======================
# RAWG API Helpers
# ======================
def rawg_fetch(endpoint, params=None):
    """Send a request to the RAWG API."""
    try:
        params = params or {}
        params["key"] = RAWG_API_KEY
        url = f"https://api.rawg.io/api/{endpoint}"
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return {"success": True, "data": response.json(), "error": None}
    except requests.exceptions.RequestException as e:
        return {"success": False, "data": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "data": None, "error": f"Unexpected error: {str(e)}"}

def simplify_games(raw_games):
    """Simplify game data to keep only relevant fields."""
    simplified = []
    for game in raw_games:
        simplified.append({
            "id": game.get("id"),
            "name": game.get("name"),
            "released": game.get("released"),
            "rating": game.get("rating"),
            "metacritic": game.get("metacritic"),
            "platforms": [p["platform"]["name"] for p in game.get("platforms", [])],
            "genres": [genre["name"] for genre in game.get("genres", [])],
            "tags": [tag["name"] for tag in game.get("tags", [])][:5],  # Only first 5 tags
            "background_image": game.get("background_image")
        })
    return simplified

def format_stores(stores_data):
    """Format store information."""
    stores = []
    for store in stores_data:
        stores.append({
            "store": store["store"]["name"],
            "url": store.get("url", "No URL available"),
            "store_id": store["store"]["id"]
        })
    return stores

# ======================
# JSON-RPC Methods - RAWG Tools
# ======================
@method
async def rawg_search(query: str, page_size: int = 5):
    """Search games by name on RAWG."""
    try:
        if not query.strip():
            return Error(code=-1, message="Query cannot be empty")
        
        log_message("user", f"Searching games: {query}")
        
        response = rawg_fetch("games", {
            "search": query,
            "page_size": min(page_size, 20),
            "search_precise": "true"
        })
        
        if not response["success"]:
            return Error(code=-1, message=f"RAWG API error: {response['error']}")
        
        games = simplify_games(response["data"].get("results", []))
        result_msg = f"Found {len(games)} games for '{query}'"
        
        log_message("assistant", result_msg)
        
        return Success({
            "success": True,
            "message": result_msg,
            "query": query,
            "count": len(games),
            "games": games
        })
        
    except Exception as e:
        error_msg = f"Error searching games: {str(e)}"
        log_message("assistant", error_msg)
        return Error(code=-1, message=error_msg)

@method
async def rawg_popular(page_size: int = 10):
    """Get the most popular games from RAWG."""
    try:
        log_message("user", "Fetching popular games")
        
        response = rawg_fetch("games", {
            "ordering": "-added",
            "page_size": min(page_size, 20)
        })
        
        if not response["success"]:
            return Error(code=-1, message=f"RAWG API error: {response['error']}")
        
        games = simplify_games(response["data"].get("results", []))
        result_msg = f"Fetched {len(games)} popular games"
        
        log_message("assistant", result_msg)
        
        return Success({
            "success": True,
            "message": result_msg,
            "count": len(games),
            "games": games
        })
        
    except Exception as e:
        error_msg = f"Error fetching popular games: {str(e)}"
        log_message("assistant", error_msg)
        return Error(code=-1, message=error_msg)

@method
async def rawg_by_genre(genre: str, page_size: int = 10):
    """Get games filtered by genre."""
    try:
        if not genre.strip():
            return Error(code=-1, message="Genre cannot be empty")
        
        log_message("user", f"Searching games by genre: {genre}")
        
        response = rawg_fetch("games", {
            "genres": genre.lower(),
            "page_size": min(page_size, 20),
            "ordering": "-rating"
        })
        
        if not response["success"]:
            return Error(code=-1, message=f"RAWG API error: {response['error']}")
        
        games = simplify_games(response["data"].get("results", []))
        result_msg = f"Found {len(games)} games in genre '{genre}'"
        
        log_message("assistant", result_msg)
        
        return Success({
            "success": True,
            "message": result_msg,
            "genre": genre,
            "count": len(games),
            "games": games
        })
        
    except Exception as e:
        error_msg = f"Error fetching games by genre: {str(e)}"
        log_message("assistant", error_msg)
        return Error(code=-1, message=error_msg)

@method
async def rawg_by_platform(platform: str, page_size: int = 10):
    """Get games filtered by platform."""
    try:
        if not platform.strip():
            return Error(code=-1, message="Platform cannot be empty")
        
        log_message("user", f"Searching games by platform: {platform}")
        
        response = rawg_fetch("games", {
            "platforms": platform.lower(),
            "page_size": min(page_size, 20),
            "ordering": "-rating"
        })
        
        if not response["success"]:
            return Error(code=-1, message=f"RAWG API error: {response['error']}")
        
        games = simplify_games(response["data"].get("results", []))
        result_msg = f"Found {len(games)} games for platform '{platform}'"
        
        log_message("assistant", result_msg)
        
        return Success({
            "success": True,
            "message": result_msg,
            "platform": platform,
            "count": len(games),
            "games": games
        })
        
    except Exception as e:
        error_msg = f"Error fetching games by platform: {str(e)}"
        log_message("assistant", error_msg)
        return Error(code=-1, message=error_msg)

@method
async def rawg_game_details(game_name: str):
    """Get detailed info for a specific game."""
    try:
        if not game_name.strip():
            return Error(code=-1, message="Game name cannot be empty")
        
        log_message("user", f"Fetching details for game: {game_name}")
        
        search_response = rawg_fetch("games", {
            "search": game_name,
            "page_size": 1,
            "search_precise": "true"
        })
        
        if not search_response["success"] or not search_response["data"].get("results"):
            return Error(code=-1, message=f"Game '{game_name}' not found")
        
        game_id = search_response["data"]["results"][0]["id"]
        
        details_response = rawg_fetch(f"games/{game_id}")
        
        if not details_response["success"]:
            return Error(code=-1, message=f"Error fetching details: {details_response['error']}")
        
        game_data = details_response["data"]
        
        game_details = {
            "id": game_data.get("id"),
            "name": game_data.get("name"),
            "description": game_data.get("description_raw", "")[:500] + "..." if game_data.get("description_raw") else "No description",
            "released": game_data.get("released"),
            "rating": game_data.get("rating"),
            "metacritic": game_data.get("metacritic"),
            "playtime": game_data.get("playtime", 0),
            "developers": [dev["name"] for dev in game_data.get("developers", [])],
            "publishers": [pub["name"] for pub in game_data.get("publishers", [])],
            "genres": [genre["name"] for genre in game_data.get("genres", [])],
            "platforms": [p["platform"]["name"] for p in game_data.get("platforms", [])],
            "esrb_rating": game_data.get("esrb_rating", {}).get("name", "Not Rated"),
            "website": game_data.get("website", ""),
            "background_image": game_data.get("background_image")
        }
        
        result_msg = f"Details fetched for '{game_name}'"
        log_message("assistant", result_msg)
        
        return Success({
            "success": True,
            "message": result_msg,
            "game": game_details
        })
        
    except Exception as e:
        error_msg = f"Error fetching game details: {str(e)}"
        log_message("assistant", error_msg)
        return Error(code=-1, message=error_msg)

@method
async def rawg_game_stores(game_name: str):
    """Get stores where a specific game is sold."""
    try:
        if not game_name.strip():
            return Error(code=-1, message="Game name cannot be empty")
        
        log_message("user", f"Fetching stores for: {game_name}")
        
        search_response = rawg_fetch("games", {
            "search": game_name,
            "page_size": 1,
            "search_precise": "true"
        })
        
        if not search_response["success"] or not search_response["data"].get("results"):
            return Error(code=-1, message=f"Game '{game_name}' not found")
        
        game_id = search_response["data"]["results"][0]["id"]
        
        stores_response = rawg_fetch(f"games/{game_id}/stores")
        
        if not stores_response["success"]:
            return Error(code=-1, message=f"Error fetching stores: {stores_response['error']}")
        
        stores = format_stores(stores_response["data"].get("results", []))
        result_msg = f"Found {len(stores)} stores for '{game_name}'"
        
        log_message("assistant", result_msg)
        
        return Success({
            "success": True,
            "message": result_msg,
            "game_name": game_name,
            "stores": stores
        })
        
    except Exception as e:
        error_msg = f"Error fetching stores: {str(e)}"
        log_message("assistant", error_msg)
        return Error(code=-1, message=error_msg)

@method
async def rawg_game_dlcs(game_name: str, page_size: int = 10):
    """Get DLCs/expansions for a specific game."""
    try:
        if not game_name.strip():
            return Error(code=-1, message="Game name cannot be empty")
        
        log_message("user", f"Fetching DLCs for: {game_name}")
        
        search_response = rawg_fetch("games", {
            "search": game_name,
            "page_size": 1,
            "search_precise": "true"
        })
        
        if not search_response["success"] or not search_response["data"].get("results"):
            return Error(code=-1, message=f"Game '{game_name}' not found")
        
        game_id = search_response["data"]["results"][0]["id"]
        
        dlc_response = rawg_fetch(f"games/{game_id}/additions", {
            "page_size": min(page_size, 20)
        })
        
        if not dlc_response["success"]:
            return Error(code=-1, message=f"Error fetching DLCs: {dlc_response['error']}")
        
        dlcs = simplify_games(dlc_response["data"].get("results", []))
        result_msg = f"Found {len(dlcs)} DLCs for '{game_name}'"
        
        log_message("assistant", result_msg)
        
        return Success({
            "success": True,
            "message": result_msg,
            "game_name": game_name,
            "dlcs": dlcs
        })
        
    except Exception as e:
        error_msg = f"Error fetching DLCs: {str(e)}"
        log_message("assistant", error_msg)
        return Error(code=-1, message=error_msg)

@method
async def list_tools():
    """List available tools on the RAWG server."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "rawg_search",
                "description": "Search for games by name in the RAWG database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Name of the game to search"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of results to return (max 20)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rawg_popular",
                "description": "Retrieve a list of popular games",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Number of games to retrieve (max 20)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rawg_by_genre",
                "description": "Search games filtered by a specific genre",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "genre": {
                            "type": "string",
                            "description": "Game genre (e.g., action, rpg, strategy, shooter)"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of games to return (max 20)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": ["genre"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rawg_by_platform",
                "description": "Search games filtered by a specific platform",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "Platform name (e.g., pc, playstation-5, xbox-series-x, nintendo-switch)"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of games to return (max 20)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": ["platform"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rawg_game_details",
                "description": "Get detailed information about a specific game",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "game_name": {
                            "type": "string",
                            "description": "Exact name of the game"
                        }
                    },
                    "required": ["game_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rawg_game_stores",
                "description": "Retrieve stores where a specific game can be purchased",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "game_name": {
                            "type": "string",
                            "description": "Name of the game"
                        }
                    },
                    "required": ["game_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rawg_game_dlcs",
                "description": "Retrieve DLCs or expansions for a specific game",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "game_name": {
                            "type": "string",
                            "description": "Base game name"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of DLCs to return (max 20)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": ["game_name"]
                }
            }
        }
    ]
    return Success({"status": "ok", "tools": tools})


# ======================
# JSON-RPC Endpoint
# ======================
@app.post("/")
async def handle(request: Request):
    data = await request.body()
    response = await dispatch(data.decode("utf-8"))
    return JSONResponse(content=json.loads(str(response)))

# ======================
# Health Check
# ======================
@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "message": "RAWG MCP Server is running",
        "api_key_configured": bool(RAWG_API_KEY)
    }

# ======================
# Info Endpoint
# ======================
@app.get("/info")
async def info():
    return {
        "name": "RAWG MCP Server",
        "version": "1.0.0",
        "description": "MCP server to access RAWG Video Games Database",
        "methods": [
            "rawg_search", "rawg_popular", "rawg_by_genre", "rawg_by_platform",
            "rawg_game_details", "rawg_game_stores", "rawg_game_dlcs"
        ]
    }

# ======================
# Main
# ======================
if __name__ == "__main__":
    import uvicorn
    print("Starting RAWG MCP Server on http://localhost:8003")
    print(f"RAWG API Key configured: {'YES' if RAWG_API_KEY else 'NO'}")
    uvicorn.run(app, host="0.0.0.0", port=8003)
