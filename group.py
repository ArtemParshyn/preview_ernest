import os
from pathlib import Path
from django.core.files import File
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'preview.settings')
django.setup()

from back.models import Item, Group, ApiUser

# Define the path to your image directory

# Iterate through all files in the directory
for i in ['Vienvietė', 'Didesnė', 'Priedai']:
    user_for = ApiUser.objects.get(username='123')
    Group.objects.create(name=i, user_for=user_for)
