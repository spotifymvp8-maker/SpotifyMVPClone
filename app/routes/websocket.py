"""WebSocket routes."""

import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.message import Message
from app.models.user_status import UserStatus
from app.websocket import manager   # глобальный ConnectionManager (singleton)
from app.utils import decode_token

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint для real-time функциональности.

    Обрабатывает два типа сообщений от клиента:
        1. send_message    — личное сообщение другому пользователю
        2. update_activity — обновление текущей активности (что слушает)

    Жизненный цикл соединения:
        1. Проверка токена → подключение → рассылка онлайн-статусов
        2. Бесконечный цикл приёма сообщений
        3. Отключение → обновление статуса → уведомление остальных

    WebSocket и авторизация:
        Стандартный HTTP-заголовок Authorization не поддерживается в WS.
        Клиент передаёт токен через параметры соединения (websocket.scope["auth"]).
    """

    # ── Шаг 1: Аутентификация ──
    auth = websocket.scope.get("auth", {})
    user_id_str = auth.get("userId")
    token = auth.get("token", "")

    # Убираем префикс "Bearer " если клиент его передал
    if token.startswith("Bearer "):
        token = token[7:]

    # Декодируем JWT — проверяем подпись и срок жизни
    payload = decode_token(token)

    if not payload or not user_id_str:
        # Закрываем соединение с кодом 4001 (кастомный код "Unauthorized")
        await websocket.close(code=4001, reason="Invalid authentication")
        return

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        await websocket.close(code=4001, reason="Invalid user ID")
        return

    # ── Шаг 2: Подключение пользователя ──
    # manager.connect принимает WebSocket и добавляет его в active_connections[user_id]
    await manager.connect(websocket, user_id)

    # Обновляем статус в БД (is_online = True)
    user_status = db.query(UserStatus).filter(UserStatus.user_id == user_id).first()
    if not user_status:
        user_status = UserStatus(user_id=user_id, is_online=True)
        db.add(user_status)
    else:
        user_status.is_online = True
    db.commit()

    # ── Шаг 3: Приветственные сообщения ──
    # Отправляем подключившемуся пользователю подтверждение
    await manager.send_personal_message({"type": "connected", "userId": str(user_id)}, user_id)

    # Рассылаем всем обновлённый список онлайн-пользователей
    await manager.broadcast_online_users()

    # Рассылаем всем текущие активности (кто что слушает)
    await manager.broadcast_activities()

    # ── Шаг 4: Основной цикл приёма сообщений ──
    try:
        while True:
            # Ждём сообщение от клиента (блокирует до получения)
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")

            # ── Обработка личного сообщения ──
            if message_type == "send_message":
                receiver_id_str = message.get("receiverId")
                content = message.get("content")

                if not receiver_id_str or not content:
                    continue  # игнорируем неполные сообщения

                try:
                    receiver_id = UUID(receiver_id_str)
                except ValueError:
                    continue

                # Сохраняем сообщение в БД (для истории переписки)
                db_message = Message(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    content=content
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)

                # Формируем payload сообщения для отправки
                msg_payload = {
                    "id": str(db_message.id),
                    "sender_id": str(db_message.sender_id),
                    "receiver_id": str(db_message.receiver_id),
                    "content": db_message.content,
                    "created_at": db_message.created_at.isoformat(),
                    "updated_at": db_message.updated_at.isoformat(),
                }

                # Отправляем получателю (если он онлайн — придёт сразу через WS)
                await manager.send_message_to_user(
                    {"type": "receive_message", "message": msg_payload}, receiver_id
                )

                # Подтверждаем отправителю, что сообщение доставлено
                await manager.send_personal_message(
                    {"type": "message_sent", "message": msg_payload}, user_id
                )

            # ── Обработка обновления активности ──
            elif message_type == "update_activity":
                activity = message.get("activity")
                if activity:
                    # Обновляем в памяти менеджера (для быстрой рассылки)
                    manager.update_activity(user_id, activity)

                    # Обновляем в БД (для персистентности — сохранится при перезапуске)
                    user_status = db.query(UserStatus).filter(
                        UserStatus.user_id == user_id
                    ).first()
                    if user_status:
                        user_status.current_activity = activity
                        db.commit()

                    # Рассылаем всем обновлённую активность
                    await manager.broadcast({
                        "type": "activity_updated",
                        "userId": str(user_id),
                        "activity": activity
                    })

    # ── Шаг 5: Отключение пользователя ──
    except WebSocketDisconnect:
        # Удаляем из active_connections и online_users в менеджере
        manager.disconnect(user_id, websocket)

        # Обновляем статус в БД
        user_status = db.query(UserStatus).filter(UserStatus.user_id == user_id).first()
        if user_status:
            user_status.is_online = False
            db.commit()

        # Уведомляем остальных об отключении и обновляем список онлайн
        await manager.broadcast({"type": "user_disconnected", "userId": str(user_id)})
        await manager.broadcast_online_users()
