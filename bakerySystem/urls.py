from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authviews
from bakerySystem import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, base_name = 'user')
router.register(r'customers', views.CustomerViewSet, base_name = 'customer')
router.register(r'shops', views.ShopViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'getItem', views.getItem)
router.register(r'getnearshop', views.getNearShop)


urlpatterns = [
	path('', include(router.urls)),
	
	
	# 탐색 가능한 API를 위한 로그인/로그아웃 뷰
	path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	path('api-token-auth/', authviews.obtain_auth_token),
	path('pushNotifyAll/<title>/<bodymsg>/', views.pushNotifyAll),
]