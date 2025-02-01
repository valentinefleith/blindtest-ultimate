from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rooms import (
    generate_room_code,
    authenticate_websocket,
    remove_player_from_room,
    broadcast_players,
    active_rooms,
    room_owners,
)

router = APIRouter()


@router.websocket("/ws/create")
async def create_room(websocket: WebSocket, db: Session = Depends(get_db)):
    """Crée une nouvelle room et génère un code d'accès."""
    await websocket.accept()

    user = await authenticate_websocket(websocket, db)
    if user is None:
        return
    # ✅ Génération du code de la room
    room_code = generate_room_code()
    while room_code in active_rooms:
        room_code = generate_room_code()

    # ✅ Création de la room avec le créateur dedans
    active_rooms[room_code] = {user.username: websocket}
    room_owners[room_code] = user.username
    # room_status[room_code] = "waiting"

    # ✅ Envoi du code au créateur
    await websocket.send_json({"action": "room_created", "room_code": room_code})
    print(f"Room {room_code} créée par {user.username}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message recu de {user.username}: {data}")
    except WebSocketDisconnect:
        await remove_player_from_room(room_code, user.username)
        print(f"{user.username} a quitté la room {room_code}")


@router.websocket("/ws/join/{room_code}")
async def join_room(
    websocket: WebSocket, room_code: str, db: Session = Depends(get_db)
):
    """Permet de rejoindre une room via son code."""

    await websocket.accept()
    # ✅ Récupérer le token JWT depuis les paramètres de l'URL
    user = await authenticate_websocket(websocket, db)
    if user is None:
        return

    if room_code not in active_rooms:
        await websocket.send_json({"error": "Room not found"})
        await websocket.close()
        return

    # Decommenter pour bloquer la room une fois la partie lancee
    # if room_status.get(room_code) == "started":
    #     await websocket.send_json({"error": "The game has already started"})
    #     await websocket.close()
    #     return

    if user.username in active_rooms[room_code]:
        await websocket.send_json({"error": "You are already in this room"})
        await websocket.close()
        return

    active_rooms[room_code][user.username] = websocket
    await broadcast_players(room_code)
    print(f"{user.username} a rejoint la room {room_code}")

    # Notifier tout le monde
    # for player_ws in active_rooms[room_code].values():
    #     await player_ws.send_json(
    #         {"action": "player_joined", "username": user.username}
    #     )
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message recu de {user.username}: {data}")
    except WebSocketDisconnect:
        await remove_player_from_room(room_code, user.username)
        print(f"{user.username} a quitté la room {room_code}")


@router.websocket("/ws/start/{room_code}")
async def start_game(
    websocket: WebSocket, room_code: str, db: Session = Depends(get_db)
):
    """Permet au chef de la room de démarrer la partie."""
    await websocket.accept()

    user = await authenticate_websocket(websocket, db)
    if user is None:
        return

    # ✅ Vérifier que la room existe
    if room_code not in active_rooms:
        await websocket.send_json({"error": "Room not found"})
        await websocket.close()
        return

    # ✅ Vérifier que l'utilisateur est le chef de la room
    if room_owners.get(room_code) != user.username:
        await websocket.send_json({"error": "Only the room owner can start the game"})
        await websocket.close()
        return

    # room_status[room_code] = "started"

    # ✅ Notifier tous les joueurs que la partie commence
    start_message = {"action": "game_started", "message": "The game has started!"}
    for player_ws in active_rooms[room_code].values():
        await player_ws.send_json(start_message)

    print(f"🎮 La partie a commencé dans la room {room_code} par {user.username}")
