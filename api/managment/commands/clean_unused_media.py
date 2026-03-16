import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps

from your_app.models import ApiUser, Previews, Item  # замените your_app на имя вашего приложения


class Command(BaseCommand):
    help = 'Удаляет неиспользуемые медиафайлы из папки media/'

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            self.stdout.write(self.style.ERROR("Папка MEDIA_ROOT не существует."))
            return

        # Собираем все пути к используемым изображениям
        used_files = set()

        # ApiUser.logo
        for user in ApiUser.objects.exclude(logo='').only('logo'):
            if user.logo:
                used_files.add(user.logo.path)

        # Previews.image
        for preview in Previews.objects.exclude(image='').only('image'):
            if preview.image:
                used_files.add(preview.image.path)

        # Item.image
        for item in Item.objects.exclude(image='').only('image'):
            if item.image:
                used_files.add(item.image.path)

        # Преобразуем в абсолютные пути (на всякий случай)
        used_files = {os.path.abspath(f) for f in used_files}

        # Проходим по всем файлам в MEDIA_ROOT
        deleted_count = 0
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                if file_path not in used_files:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        self.stdout.write(f"Удалён: {file_path}")
                    except OSError as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка при удалении {file_path}: {e}"))

        self.stdout.write(
            self.style.SUCCESS(f"Очистка завершена. Удалено файлов: {deleted_count}")
        )