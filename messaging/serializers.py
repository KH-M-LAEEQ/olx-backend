from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    is_mine     = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ('id', 'sender_name', 'is_mine', 'body', 'is_read', 'created_at')

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and obj.sender_id == request.user.id)


class ConversationListSerializer(serializers.ModelSerializer):
    ad_title     = serializers.CharField(source='ad.title', read_only=True)
    ad_id        = serializers.IntegerField(source='ad.id', read_only=True)
    ad_cover     = serializers.SerializerMethodField()
    other_user   = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ('id', 'ad_id', 'ad_title', 'ad_cover', 'other_user',
                  'last_message', 'unread_count', 'updated_at')

    def get_ad_cover(self, obj):
        request = self.context.get('request')
        cover = obj.ad.images.filter(is_cover=True).first() or obj.ad.images.first()
        if cover and request:
            return request.build_absolute_uri(cover.image.url)
        return None

    def get_other_user(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        other = obj.seller if obj.buyer_id == request.user.id else obj.buyer
        return {'id': other.id, 'username': other.username}

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return {'body': msg.body[:80], 'created_at': str(msg.created_at)}
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()


class ConversationDetailSerializer(ConversationListSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationListSerializer.Meta):
        fields = ConversationListSerializer.Meta.fields + ('messages',)
