from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.routes.auth import verify_jwt_token  # Vérifie les JWTs
from app.models import User
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

active_rooms = {}  # Dictionnaire des salles et joueurs connectés


async def get_user_from_token(token: str, db: Session):
    """Vérifie le token et récupère l'utilisateur"""
    credentials_exception = HTTPException(status_code=401, detail="Invalid token")
    token_data = verify_jwt_token(token, credentials_exception)

    user = db.query(User).filter(User.id == token_data.id).first()
    if not user:
        raise credentials_exception

    return user


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: str, db: Session = Depends(get_db)
):
    """WebSocket qui oblige l'authentification via JWT et empêche plusieurs connexions du même utilisateur"""
    await websocket.accept()

    # 1️⃣ Récupérer le token JWT envoyé par le client
    query_params = websocket.query_params
    token = query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        user = await get_user_from_token(token, db)
    except HTTPException:
        await websocket.close(code=1008)
        return

    # 2️⃣ Vérifier si l'utilisateur est déjà connecté
    if room_id not in active_rooms:
        active_rooms[room_id] = {}

    if user.username in active_rooms[room_id]:
        # Déconnecte l'ancienne session avant d'ajouter la nouvelle
        old_websocket = active_rooms[room_id][user.username]
        await old_websocket.close(code=1001)  # Code 1001 = "Going Away"

    # 3️⃣ Ajouter la nouvelle connexion du joueur
    active_rooms[room_id][user.username] = websocket

    # 4️⃣ Notifier tous les joueurs de la mise à jour
    await broadcast_players(room_id)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message reçu de {user.username}: {data}")
    except WebSocketDisconnect:
        # Vérifier que la salle existe encore avant d'essayer de supprimer le joueur
        if room_id in active_rooms and user.username in active_rooms[room_id]:
            del active_rooms[room_id][user.username]

        # Notifier les autres joueurs de la déconnexion
        await broadcast_players(room_id)


async def broadcast_players(room_id: str):
    """Envoie la liste des joueurs connectés à toute la salle"""
    if room_id in active_rooms:
        players = list(active_rooms[room_id].keys())
        message = {"type": "players", "players": players}

        for player_ws in active_rooms[room_id].values():
            await player_ws.send_json(message)
