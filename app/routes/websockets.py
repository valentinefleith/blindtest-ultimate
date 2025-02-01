from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.routes.auth import get_curr_user
from sqlalchemy.orm import Session
from app.database import get_db
import secrets
import string

router = APIRouter()

active_rooms = {}  # Dictionnaire des salles et joueurs connectés


def generate_room_code(length=6):
    """Génère un code de room aléatoire."""
    alphabet = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.websocket("/ws/create")
async def create_room(websocket: WebSocket, db: Session = Depends(get_db)):
    """Crée une nouvelle room et génère un code d'accès."""
    await websocket.accept()

    # ✅ Récupérer le token JWT depuis les paramètres de l'URL
    query_params = websocket.query_params
    token = query_params.get("token")

    if not token:
        await websocket.close(code=1008)  # Unauthorized
        return

    try:
        user = get_curr_user(token, db)  # ✅ Vérification manuelle du token
    except HTTPException:
        await websocket.close(code=1008)
        return

    # ✅ Génération du code de la room
    room_code = generate_room_code()
    while room_code in active_rooms:
        room_code = generate_room_code()

    # ✅ Création de la room avec le créateur dedans
    active_rooms[room_code] = {user.username: websocket}

    # ✅ Envoi du code au créateur
    await websocket.send_json({"action": "room_created", "room_code": room_code})
    print(f"Room {room_code} créée par {user.username}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message recu de {user.username}: {data}")
            # Ici, gérer les messages de la room
    except WebSocketDisconnect:
        del active_rooms[room_code][user.username]
        if not active_rooms[room_code]:  # Supprime la room si plus personne dedans
            del active_rooms[room_code]
        print(f"{user.username} a quitté la room {room_code}")


@router.websocket("/ws/join/{room_code}")
async def join_room(
    websocket: WebSocket, room_code: str, db: Session = Depends(get_db)
):
    """Permet de rejoindre une room via son code."""

    # ✅ Récupérer le token JWT depuis les paramètres de l'URL
    query_params = websocket.query_params
    token = query_params.get("token")

    if not token:
        await websocket.close(code=1008)  # Unauthorized
        return

    try:
        user = get_curr_user(token, db)  # ✅ Vérification manuelle du token
    except HTTPException:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    if room_code not in active_rooms:
        await websocket.send_json({"error": "Room not found"})
        await websocket.close()
        return

    if user.username in active_rooms[room_code]:
        await websocket.send_json({"error": "You are already in this room"})
        await websocket.close()
        return

    active_rooms[room_code][user.username] = websocket

    # Notifier tout le monde
    for player_ws in active_rooms[room_code].values():
        await player_ws.send_json(
            {"action": "player_joined", "username": user.username}
        )

    print(f"{user.username} a rejoint la room {room_code}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message recu de {user.username}: {data}")
    except WebSocketDisconnect:
        if room_code in active_rooms and user.username in active_rooms[room_code]:
            del active_rooms[room_code][user.username]
        if not active_rooms[room_code]:
            del active_rooms[room_code]
        print(f"{user.username} a quitté la room {room_code}")


async def broadcast_players(room_id: str):
    """Envoie la liste des joueurs connectés à toute la salle"""
    if room_id in active_rooms:
        players = list(active_rooms[room_id].keys())
        message = {"type": "players", "players": players}

        for player_ws in active_rooms[room_id].values():
            await player_ws.send_json(message)
