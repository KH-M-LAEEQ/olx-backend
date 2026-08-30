import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import Conversation, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conv_id = self.scope['url_route']['kwargs']['conv_id']
        self.group_name = f'conversation_{self.conv_id}'

        self.user = await self._authenticate()
        if not self.user:
            await self.close(code=4001)
            return

        if not await self._is_participant():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            body = (json.loads(text_data).get('body') or '').strip()
        except (json.JSONDecodeError, AttributeError):
            return
        if not body:
            return

        msg_data = await self._save_message(body)
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'chat_message', 'message': msg_data}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _token_from_query(self):
        qs = self.scope.get('query_string', b'').decode()
        for part in qs.split('&'):
            if part.startswith('token='):
                return part[6:]
        return None

    @database_sync_to_async
    def _authenticate(self):
        token = self._token_from_query()
        if not token:
            return None
        try:
            payload = AccessToken(token)
            return User.objects.get(id=payload['user_id'])
        except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
            return None

    @database_sync_to_async
    def _is_participant(self):
        try:
            conv = Conversation.objects.only('buyer_id', 'seller_id').get(pk=self.conv_id)
            return self.user.id in (conv.buyer_id, conv.seller_id)
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def _save_message(self, body):
        conv = Conversation.objects.get(pk=self.conv_id)
        msg = Message.objects.create(conversation=conv, sender=self.user, body=body)
        conv.save()
        return {
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.username,
            'body': msg.body,
            'is_read': msg.is_read,
            'created_at': msg.created_at.isoformat(),
        }
