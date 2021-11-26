from rest_framework import routers
from filemanager.viewsets import DataViewSet

router = routers.DefaultRouter()
router.register(r'files', DataViewSet, basename='data')   #basename 或者 base_name 取决于版本
