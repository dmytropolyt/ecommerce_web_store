from django.db import models
from django.urls import reverse
from category.models import Category
from django.contrib.auth import get_user_model
from django.db.models import Avg

import os


User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    users_wishlist = models.ManyToManyField(User, related_name='wishlist', blank=True)

    def get_url(self):
        return reverse('store:product-detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.name

    def average_review(self):
        reviews = self.review.aggregate(average=Avg('rating'))
        return reviews['average'] if reviews['average'] else 0


class VariationManager(models.Manager):
    def colors(self):
        return super().filter(category='color', is_active=True)

    def sizes(self):
        return super().filter(category='size', is_active=True)


category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=category_choice)
    value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, related_name='review', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.GenericIPAddressField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):

    def image_upload_to(self, instance=None):
        if instance:
            return os.path.join('store/products', self.product.name, instance)
        return None

    product = models.ForeignKey(Product, related_name='gallery', default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to, max_length=255)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'


# class WishList(models.Model):
#     user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, related_name='wishlist', on_delete=models.CASCADE)
#
#     class Meta:
#         unique_together = ['user', 'product']
