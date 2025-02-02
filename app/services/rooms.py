import secrets
import string
from fastapi import WebSocket, HTTPException, APIRouter
from app.routes.auth import get_curr_user
from sqlalchemy.orm import Session

# Dictionnaires pour gérer les rooms
active_rooms = {}  # Room ID -> {username: websocket}
room_owners = {}  # Room ID -> owner_username
# room_status = {}   # Room ID -> "waiting" | "started"

router = APIRouter()


@router.get("/rooms/exists/{room_code}")
def check_room_exists(room_code: str):
    """Check if a room exists before allowing a user to join."""
    print(f"🔍 Checking if room exists: {room_code}")  # Debugging

    # Print all current rooms
    print(f"📋 Active Rooms: {list(active_rooms.keys())}")

    if room_code in active_rooms:
        print(f"✅ Room {room_code} exists!")
        return {"exists": True}

    print(f"❌ Room {room_code} not found!")
    raise HTTPException(status_code=404, detail="Room not found")


def generate_room_code(length=6):
    """Génère un code de room aléatoire."""
    alphabet = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def authenticate_websocket(websocket: WebSocket, db: Session):
    query_params = websocket.query_params
    token = query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return None

    try:
        return get_curr_user(token, db)
    except HTTPException:
        await websocket.close(code=1008)
        return None


async def remove_player_from_room(room_code: str, username: str):
    """Gère la déconnexion d'un joueur."""
    if room_code in active_rooms and username in active_rooms[room_code]:
        del active_rooms[room_code][username]

    # Si plus personne dans la room, la supprimer
    if not active_rooms.get(room_code):
        del active_rooms[room_code]
        del room_owners[room_code]
        # if room_code in room_status:
        #     del room_status[room_code]


async def broadcast_players(room_id: str):
    """Envoie la liste des joueurs connectés à toute la salle"""
    if room_id in active_rooms:
        players = list(active_rooms[room_id].keys())
        message = {"type": "players", "players": players}

        for player_ws in active_rooms[room_id].values():
            await player_ws.send_json(message)
