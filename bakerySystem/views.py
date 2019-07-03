from django.shortcuts import render

from rest_framework import viewsets, permissions, renderers, generics
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db.models.expressions import RawSQL
import math
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.http import HttpResponse

from bakerySystem.models import User, Customer, Shop, Item
from bakerySystem.serializers import UserSerializer, CustomerSerializer, ShopSerializer, ItemSerializer
from bakerySystem.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, ItemPermissions


# Create your views here.
"""
이 뷰셋은 `list`와 `detail` 기능을 자동으로 지원합니다
"""
class UserViewSet(viewsets.ModelViewSet):
	serializer_class = UserSerializer
	permission_classes = (IsOwnerOrAdmin, )
	class Meta:
		model = User
	
	def get_queryset(self):
		user = self.request.user
		return User.objects.filter(username=user)
	
class CustomerViewSet(viewsets.ModelViewSet):
	queryset = Customer.objects.all()
	serializer_class = CustomerSerializer
	
	#permission_classes = (IsOwnerOrAdmin,)
	
	class Meta:
		model = Customer
	
	def get_queryset(self):
		requestuser = self.request.user
		return Customer.objects.filter(user=requestuser)


"""
이 뷰셋은 `list`와 `create`, `retrieve`, `update`, 'destroy` 기능을 자동으로 지원
여기에 `highlight` 기능의 코드만 추가로 작성

#GET => DB에 저장된 해당 pk데이터 출력(조회)
#POST => 넘어온 값 DB에 저장
#PUT => 해당 pk데이터를 넘어온 값으로 업데이트
#DELETE => 해당 pk데이터 삭제
"""
class ShopViewSet(viewsets.ModelViewSet):
	queryset = Shop.objects.all()
	serializer_class = ShopSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
			
	def perform_create(self, serializer):
		serializer.save(owner = self.request.user)
		
class ItemViewSet(viewsets.ModelViewSet):	
	queryset = Item.objects.all()
	serializer_class = ItemSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, ItemPermissions,)
		
	def perform_create(self, serializer):
		getUser = self.request.user
		myshop = Shop.objects.filter(owner = getUser)
		serializer.save(shop = myshop[0])

	@list_route()
	def getShopItem(self, request):
		params = request.query_params['shopName']
		myshop = Shop.objects.filter(name = params)
		itemList = Item.objects.filter(shop = myshop[0])
		return Response(itemList)
		
class getItem(viewsets.ModelViewSet):
	serializer_class = ItemSerializer
	queryset = Item.objects.all()
	def get_queryset(self):
		req = self.request
		shopName = req.query_params.get('shopName')
		if shopName:
			myshop = Shop.objects.filter(name = shopName)
			self.queryset = Item.objects.filter(shop = myshop[0])
			return self.queryset
		else:
			return self.queryset
			
		
class getNearShop(viewsets.ModelViewSet):
	serializer_class = ShopSerializer
	queryset = Shop.objects.all()
	
	@receiver(connection_created)
	def extend_sqlite(connection=None, **kwargs):
		if connection.vendor == "sqlite":
			# sqlite doesn't natively support math functions, so add them
			cf = connection.connection.create_function
			cf('acos', 1, math.acos)
			cf('cos', 1, math.cos)
			cf('radians', 1, math.radians)
			cf('sin', 1, math.sin)
			
	def get_locations_nearby_coords(self, latitude, longitude, max_distance=2):
		"""
		Return objects sorted by distance to specified coordinates
		which distance is less than max_distance given in kilometers
		35.899639, 128.856356
		"""
		# Great circle distance formula
		gcd_formula = "6371 * acos(cos(radians(%s)) * \
		cos(radians(latitude)) \
		* cos(radians(longitude) - radians(%s)) + \
		sin(radians(%s)) * sin(radians(latitude)))"
		distance_raw_sql = RawSQL(gcd_formula,(latitude, longitude, latitude,))

		return distance_raw_sql
	
	def get_queryset(self):
		req = self.request
		params = req.query_params.get('userGPS')
		if params: 
			lat, lon = params.split(',')
			
			distance_raw_sql = self.get_locations_nearby_coords(float(lat), float(lon))
			self.queryset = Shop.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
			return self.queryset
			
		else:
			return self.queryset
			
def pushNotifyUser(name, progress, work):
	from pusher_push_notifications import PushNotifications

	beams_client = PushNotifications(
		instance_id='a3c258e1-27c2-4053-88a1-6d644fbf78d5',
		secret_key='E922B25E4167019F9CA1A482F9B1689A2E90E19FC4253BD184F545C76D15D78C',
	)
	response = beams_client.publish_to_users(
		user_ids=['user-0001'],
		publish_body={
			'apns': {
				'aps': {
					'alert': 'Hello!'
				}
			},
			'fcm': {
				'notification': {
					'title': 'Hello',
					'body': 'Hello, World!'
				}
			}
		}
	)

	print(response['publishId'])
	
def pushNotifyAll(request, title, bodymsg):
	from pusher_push_notifications import PushNotifications

	beams_client = PushNotifications(
		instance_id='a3c258e1-27c2-4053-88a1-6d644fbf78d5',
		secret_key='E922B25E4167019F9CA1A482F9B1689A2E90E19FC4253BD184F545C76D15D78C',
	)
	response = beams_client.publish_to_interests(
		interests=['hello'],
		publish_body={
			'apns': {
				'aps': {
					'alert': 'alert'
				}
			},
			'fcm': {
				'notification': {
					'title': title,
					'body': bodymsg
				}
			}
		}
	)
	
	return HttpResponse("push msg")
	
	
class sendPush(viewsets.ModelViewSet):
	def get_queryset(self):
		req = self.request
		title = req.query_params.get('title')
		bodymsg = req.query_params.get('bodymsg')
		if title:
			pushNotifyAll(title, bodymsg)
			return HttpResponse("push msg")
		