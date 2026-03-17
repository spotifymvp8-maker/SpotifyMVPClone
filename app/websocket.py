"""WebSocket manager для real-time функциональности."""

import json
from typing import Dict, List, Set
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """
    Менеджер всех активных WebSocket-соединений.

    Паттерн Singleton: единственный экземпляр manager создаётся внизу файла
    и импортируется в routes/websocket.py. Это гарантирует, что все запросы
    работают с одним общим состоянием (список онлайн-пользователей и т.д.).

    Структуры данных:
        active_connections: user_id → список WebSocket
            Один пользователь может иметь несколько соединений (несколько вкладок).
            При broadcast отправляем сообщение в каждое.

        online_users: set UUID
            Быстрая проверка онлайн-статуса O(1).

        user_activities: user_id → строка активности
            Хранит "Слушает: Song Name" для каждого онлайн-пользователя.
    """

    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}
        self.online_users: Set[UUID] = set()
        self.user_activities: Dict[UUID, str] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        """
        Принять новое WebSocket-соединение.

        websocket.accept() — обязательный шаг: подтверждает WS-handshake.
        Без него клиент будет считать соединение неудавшимся.
        """
        await websocket.accept()

        # Один пользователь может иметь несколько вкладок/соединений
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.online_users.add(user_id)

        # Уведомляем всех об изменении списка онлайн
        await self.broadcast_online_users()

    def disconnect(self, user_id: UUID, websocket: WebSocket):
        """
        Закрыть одно соединение пользователя.

        Пользователь остаётся в online_users, пока у него есть
        хотя бы одно активное соединение (другая вкладка).
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            # Если все вкладки закрыты — убираем из online
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                self.online_users.discard(user_id)
                if user_id in self.user_activities:
                    del self.user_activities[user_id]

    async def send_personal_message(self, message: dict, user_id: UUID):
        """
        Отправить сообщение конкретному пользователю.
        Если у него несколько вкладок — отправляем во все.
        """
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """
        Отправить сообщение всем подключённым пользователям.

        try/except вокруг send_json — защита от ситуации когда соединение
        уже закрыто, но ещё не удалено из active_connections (race condition).
        """
        for user_id, connections in self.active_connections.items():
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except:
                    pass  # игнорируем ошибки отправки в "зависшие" соединения

    async def broadcast_online_users(self):
        """Рассылает всем актуальный список онлайн-пользователей."""
        online_list = [str(uid) for uid in self.online_users]
        await self.broadcast({"type": "users_online", "users": online_list})

    async def broadcast_activities(self):
        """Рассылает всем текущие активности пользователей (кто что слушает)."""
        activities_list = [(str(uid), activity) for uid, activity in self.user_activities.items()]
        await self.broadcast({"type": "activities", "activities": activities_list})

    async def send_message_to_user(self, message: dict, receiver_id: UUID):
        """Отправить сообщение конкретному пользователю (алиас для send_personal_message)."""
        await self.send_personal_message(message, receiver_id)

    def update_activity(self, user_id: UUID, activity: str):
        """Обновить текущую активность пользователя в памяти."""
        self.user_activities[user_id] = activity

    def get_user_activity(self, user_id: UUID) -> str | None:
        """Получить текущую активность пользователя."""
        return self.user_activities.get(user_id)


# Глобальный singleton-экземпляр менеджера.
# Импортируется в routes/websocket.py: from app.websocket import manager
# Единый для всего приложения — хранит общее состояние соединений.
manager = ConnectionManager()
