from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Định nghĩa router cho các ViewSet
router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('events', views.EventViewSet, basename='event')
router.register('tickets', views.TicketViewSet, basename='ticket')
router.register('payments', views.PaymentViewSet, basename='payment')
router.register('discount-codes', views.DiscountCodeViewSet, basename='discount-code')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('chat-messages', views.ChatMessageViewSet, basename='chat-message')

urlpatterns = [
    path('', include(router.urls)),
]