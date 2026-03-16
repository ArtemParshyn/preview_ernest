import os
import sys
import django
from pathlib import Path

# Настройка Django (подставьте имя вашего проекта вместо 'myproject')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # ← замените 'myproject' на имя вашего проекта

django.setup()

# Импортируем модели после настройки Django
from back.models import ApiUser, Previews, Item  # ← замените 'your_app' на имя вашего приложения
from django.conf import settings


def clean_unused_media():
    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.exists():
        print("Папка MEDIA_ROOT не существует:", media_root)
        return

    # Собираем все используемые файлы
    used_files = set()

    # ApiUser.logo
    for user in ApiUser.objects.exclude(logo='').only('logo'):
        if user.logo:
            used_files.add(os.path.abspath(user.logo.path))

    # Previews.image
    for preview in Previews.objects.exclude(image='').only('image'):
        if preview.image:
            used_files.add(os.path.abspath(preview.image.path))

    # Item.image
    for item in Item.objects.exclude(image='').only('image'):
        if item.image:
            used_files.add(os.path.abspath(item.image.path))

    print(f"Найдено используемых файлов: {len(used_files)}")

    # Обходим всю папку media/
    deleted_count = 0
    for root, dirs, files in os.walk(media_root):
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))
            if file_path not in used_files:
                try:
                    os.remove(file_path)
                    print(f"Удалён: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Ошибка при удалении {file_path}: {e}")

    print(f"\n✅ Очистка завершена. Удалено файлов: {deleted_count}")


if __name__ == '__main__':
    clean_unused_media()