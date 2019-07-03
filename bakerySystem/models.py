from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

# Create your models here.
class User(AbstractUser):
	USER_TYPE_CHOICES = ((1, 'customer'),(2, 'owner'),(3, 'staff'),(4, 'admin'))
	user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default = 1)
	username = models.EmailField(unique=True, null=False, max_length=254)
	def __str__(self):
		return self.username
	
#User가 생성될 때 토큰을 자동으로 생성
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)
		
class Shop(models.Model):
	owner = models.ForeignKey(User, related_name = 'owner', on_delete=models.CASCADE, default=None)
	name = models.CharField(max_length=10)
	address = models.CharField(max_length=100)
	latitude = models.FloatField()
	longitude = models.FloatField()
	description = models.CharField(max_length=1000, blank = True)
	image = models.ImageField(default='media/default_image.jpg')
	
	def __str__(self):
		return self.name
		
class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	favorite = models.ManyToManyField(Shop, related_name = 'favorited_by', blank=True)
	def __str__(self):
		return self.user.username
		
class Item(models.Model):
	shop = models.ForeignKey(Shop, related_name = 'items', on_delete=models.CASCADE)
	name = models.CharField(max_length=10)
	price = models.IntegerField(default=0)
	discount = models.IntegerField(default=0)
	picture = models.ImageField(default = 'media/default.jpg')
	description = models.CharField(max_length=100)			
	def __str__(self):
		return self.name
		
