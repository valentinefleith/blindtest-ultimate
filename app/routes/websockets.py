from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()

# Stockage des salles et des joueurs
rooms: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """Gestion d'une connexion WebSocket pour une salle donnée"""
    await websocket.accept()

    # Ajouter le joueur dans la salle
    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    # Notifier les autres joueurs
    await broadcast(room_id, f"Un joueur a rejoint la salle {room_id}.")

    try:
        while True:
            message = await websocket.receive_text()
            await broadcast(room_id, message)  # Répéter le message à tous
    except WebSocketDisconnect:
        # Retirer le joueur de la salle
        rooms[room_id].remove(websocket)
        if not rooms[room_id]:  # Si plus personne, on supprime la salle
            del rooms[room_id]
        await broadcast(room_id, f"Un joueur a quitté la salle {room_id}.")

async def broadcast(room_id: str, message: str):
    """Envoie un message à tous les joueurs de la salle"""
    for player in rooms.get(room_id, []):
        await player.send_text(message)
