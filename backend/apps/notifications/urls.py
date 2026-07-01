"""Notification URLs."""

from rest_framework.routers import DefaultRouter

from .views import NotificationTemplateViewSet, NotificationViewSet


router = DefaultRouter()
router.register(r"notification-templates", NotificationTemplateViewSet, basename="notification-template")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls
