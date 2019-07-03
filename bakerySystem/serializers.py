from rest_framework import serializers
from bakerySystem.models import User, Customer, Shop, Item
from django.contrib.auth import authenticate

class UserSerializer(serializers.HyperlinkedModelSerializer):
	#shop = serializers.HyperlinkedRelatedField(many = True, view_name='shop-detail', read_only=True)
	class Meta:
		model = User
		fields = ('username', 'password', 'user_type')
		
	def create(self, validated_data):
		password = validated_data.pop('password', None)
		instance = self.Meta.model(**validated_data)
		if password is not None:
			instance.set_password(password)
		instance.save()
		return instance
		
		
class ShopSerializer(serializers.HyperlinkedModelSerializer):
	user = UserSerializer
	image = serializers.ImageField(use_url=True)
	owner = serializers.ReadOnlyField(source='User.username')
	#items = serializers.StringRelatedField(many=True)
	items = serializers.HyperlinkedRelatedField(many=True,read_only=True,view_name='item-detail')

	class Meta:
		model = Shop
		fields = ('id', 'owner', 'name', 'address', 'image', 'description', 'items', 'latitude', 'longitude')

class CustomerSerializer(serializers.HyperlinkedModelSerializer):
	username = serializers.CharField(source='user.username')
	favorite = ShopSerializer(many=True,  read_only=True)
	favorite_detail = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Shop.objects.all(), source='favorite')

	class Meta:
		model = Customer
		fields = ('pk', 'username', 'favorite', 'favorite_detail')
		
	def create(self, validated_data):
		user_data = validated_data.pop('user')
		customer = Customer.objects.create(**validated_data)

		for user in user_data:
			user, created = User.objects.get()
			customer.user.add(user)
		return customer
	
	def update(self, instance, validated_data):
		newData = validated_data.get('favorite')
		preData = instance.favorite.all()
		
		for x in newData:
			if instance.favorite.filter(name = x).exists():
				instance.favorite.remove(x)
			else:
				instance.favorite.add(x)	
		instance.save()
		
		return instance
		
class ItemSerializer(serializers.HyperlinkedModelSerializer):
	picture = serializers.ImageField(use_url=True)
	shop = serializers.ReadOnlyField(source='Shop.name')
	class Meta:
		model = Item
		fields = ('id', 'shop', 'name', 'price', 'discount', 'picture', 'description')
		
		
		