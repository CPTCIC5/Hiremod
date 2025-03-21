from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register(r'', views.OrganizationsViewSet, basename="organizations")

urlpatterns = router.urls