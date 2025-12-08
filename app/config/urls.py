from app.api import UserViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register('', UserViewSet, basename='user')
urlpatterns = router.urls
