import json
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.db import get_async_session
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse
from app.repositories.message import save_message
from collections import defaultdict

from app.services.logger import logger

router = APIRouter()

# Хранилище подключений
active_connections = defaultdict(set)
active_user_connections = defaultdict(set)


@router.websocket("/ws/chat/{chat_id:int}/{user_id:int}")
async def chat_ws(websocket: WebSocket, chat_id: int, user_id: int, session: AsyncSession = Depends(get_async_session)):
    await websocket.accept()
    active_connections[chat_id].add(websocket)
    active_user_connections[user_id].add(websocket)

    try:
        while True:
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info(f"Client {user_id} disconnected")
                break

            try:
                logger.debug(f"Raw WebSocket data: {data}")
                msg_data = json.loads(data)

                if msg_data["type"] == "new_message":

                    # Защита от дубликатов
                    client_id = msg_data["client_id"]
                    existing = await session.execute(select(Message).where(Message.client_id == client_id))
                    if existing.scalar():
                        continue

                    # Сохраняем
                    msg = MessageCreate(
                        chat_id=chat_id,
                        sender_id=user_id,
                        text=msg_data["text"],
                        client_id=client_id,
                        read_by=[]
                    )
                    saved = await save_message(msg, session)
                    response = MessageResponse.model_validate(saved)

                    # Рассылка всем в чате
                    for connection in active_connections[chat_id]:
                        await connection.send_json(response.model_dump(mode="json"))
                    logger.info(f"Message sent by user {user_id} in chat {chat_id}")

                if msg_data["type"] == "mark_as_read":
                    message_id = msg_data["message_id"]

                    result = await session.execute(select(Message).where(Message.id == message_id))
                    msg = result.scalar_one_or_none()
                    if not msg:
                        continue

                    if msg.read_by is None:
                        msg.read_by = []

                    if user_id not in msg.read_by:
                        msg.read_by.append(user_id)

                        # Признак прочтения в приватном чате
                        if len(msg.read_by) == 1:
                            msg.is_read = True

                        print('dddddddd')
                        print(msg)
                        await session.commit()

                        # Уведомляем отправителя
                        sender_ws_set = active_user_connections.get(msg.sender_id)
                        if sender_ws_set:
                            for conn in sender_ws_set:
                                await conn.send_json({
                                    "type": "read_receipt",
                                    "message_id": message_id,
                                    "reader_id": user_id
                                })

            except WebSocketDisconnect:
                logger.info(f"Disconnected: {user_id}")
                break
            except Exception as e:
                logger.exception(f"Error in receive/send: {e}")

    finally:
        active_connections[chat_id].discard(websocket)
        active_user_connections[user_id].discard(websocket)
