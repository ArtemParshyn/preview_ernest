from django.contrib.auth.models import AbstractUser
from django.db import models



class ApiUser(AbstractUser):
    logo = models.ImageField(upload_to='media/', blank=True, null=True)
    show_prices = models.BooleanField(blank=False, null=True)
    show_sizes = models.BooleanField(blank=False, null=True)
    show_upper_button = models.BooleanField(blank=False, null=True)
    show_lower_button = models.BooleanField(blank=False, null=True)
    show_logo_on_main_page = models.BooleanField(blank=False, null=True)
    show_logo_on_preview = models.BooleanField(blank=False, null=True)
    show_lower_lower_button = models.BooleanField(blank=False, null=True)
    title_for_lower_lower_button = models.CharField(max_length=32, blank=True, null=True)
    title_for_upper_button = models.CharField(max_length=32, blank=True, null=True)
    title_for_lower_button = models.CharField(max_length=32, blank=True, null=True)
    url_for_upper_button = models.URLField(blank=True, null=True)
    url_for_lower_button = models.URLField(blank=True, null=True)
    url_for_search = models.CharField(max_length=6, null=False, blank=False, unique=True)
    url_for_lower_lower_button = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.username


class Previews(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False)
    user_for = models.ForeignKey(ApiUser, on_delete=models.CASCADE, auto_created=True)
    image = models.ImageField(upload_to='media/', blank=False, null=False)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False)
    user_for = models.ForeignKey(ApiUser, on_delete=models.CASCADE, auto_created=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    user_for = models.ForeignKey(ApiUser, on_delete=models.CASCADE, auto_created=True)
    name = models.CharField(max_length=64, default=False, null=False)
    related = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='items')
    specification = models.CharField(choices=[
        ('Paminklai', 'Paminklai'),
        ('Sonai', 'Sonai'),
        ('Takai', 'Takai'),
        ('Plokstes', 'Plokstes'),
        ('Priedai', 'Priedai')
    ], max_length=10, blank=False, null=False)
    image = models.ImageField(upload_to='media/', blank=False, null=False)
    position = models.PositiveIntegerField(default=1, blank=True)

    def __str__(self):
        return f'{self.related} {self.specification}, {self.pk}'