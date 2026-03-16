import os
from pathlib import Path
from django.core.files import File
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'preview.settings')
django.setup()

from back.models import Item, Group, ApiUser

source_dir = [
    Path("./Vienviete/Paminklai/"),
    Path("./Vienviete/Sonai/"),
    Path("./Vienviete/Takai/"),
    Path("./Vienviete/Plokstes/"),
]

a = ['Paminklai',
        'Sonai',
        'Takai',
        'Plokstes',
    ]

user = ApiUser.objects.get(username='123')
position_counter = 0
groups = Group.objects.get(name='Vienvietė', user_for=ApiUser.objects.get(username='123'))
counter = 0
for i in source_dir:

    for file_path in i.rglob("*"):
        if file_path.is_file():
            print(f"Importing: {file_path}")

            item = Item(
                length = 200,
                width = 200,
                height = 200,
                price = 200,
                user_for=user,
                name=str(position_counter),
                related=groups,
                specification=a[counter],
                position=position_counter
            )

            with file_path.open('rb') as file_content:
                item.image.save(
                    file_path.name,  # Use original filename
                    File(file_content),  # Wrap content in Django File object
                    save=True  # Save both file and model instance
                )

            position_counter += 1

    counter += 1

print(f"Successfully imported {position_counter} items.")