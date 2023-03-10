from django.db import models
from django.urls import reverse
from category.models import Category
from django.contrib.auth import get_user_model
from django.db.models import Avg


User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

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