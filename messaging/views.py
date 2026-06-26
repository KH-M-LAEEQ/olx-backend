from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from ads.models import Ad
from .models import Conversation, Message
from .serializers import ConversationListSerializer, ConversationDetailSerializer, MessageSerializer


class ConversationListCreateView(ListAPIView):
    serializer_class   = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects
            .filter(Q(buyer=user) | Q(seller=user))
            .select_related('buyer', 'seller', 'ad')
            .prefetch_related('messages', 'ad__images')
            .order_by('-updated_at')
        )

    def post(self, request):
        ad_id = request.data.get('ad_id')
        body  = (request.data.get('body') or '').strip()
        if not ad_id or not body:
            return Response({'detail': 'ad_id and body are required.'}, status=400)

        ad = get_object_or_404(Ad, pk=ad_id, is_active=True)
        if ad.seller_id == request.user.id:
            return Response({'detail': 'You cannot message yourself.'}, status=400)

        conv, created = Conversation.objects.get_or_create(
            ad=ad, buyer=request.user,
            defaults={'seller': ad.seller}
        )
        Message.objects.create(conversation=conv, sender=request.user, body=body)
        conv.save()

        serializer = ConversationDetailSerializer(conv, context={'request': request})
        return Response(serializer.data, status=201 if created else 200)


class ConversationDetailView(RetrieveAPIView):
    serializer_class   = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from rest_framework.exceptions import PermissionDenied
        conv = get_object_or_404(
            Conversation.objects
            .select_related('buyer', 'seller', 'ad')
            .prefetch_related('messages__sender', 'ad__images'),
            pk=self.kwargs['pk']
        )
        if self.request.user not in [conv.buyer, conv.seller]:
            raise PermissionDenied
        conv.messages.filter(is_read=False).exclude(sender=self.request.user).update(is_read=True)
        return conv


class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk)
        if request.user not in [conv.buyer, conv.seller]:
            return Response({'detail': 'Forbidden.'}, status=403)
        body = (request.data.get('body') or '').strip()
        if not body:
            return Response({'detail': 'Message body is required.'}, status=400)
        msg = Message.objects.create(conversation=conv, sender=request.user, body=body)
        conv.save()
        return Response(MessageSerializer(msg, context={'request': request}).data, status=201)


class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = (
            Message.objects
            .filter(
                Q(conversation__buyer=request.user) | Q(conversation__seller=request.user),
                is_read=False
            )
            .exclude(sender=request.user)
            .count()
        )
        return Response({'unread': count})
