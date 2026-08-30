from django.urls import path
from .views import ConversationListCreateView, ConversationDetailView, SendMessageView, UnreadCountView

urlpatterns = [
    path('',                ConversationListCreateView.as_view(), name='conversations'),
    path('<int:pk>/',       ConversationDetailView.as_view(),     name='conversation-detail'),
    path('<int:pk>/reply/', SendMessageView.as_view(),            name='send-message'),
    path('unread/',         UnreadCountView.as_view(),            name='unread-count'),
]
