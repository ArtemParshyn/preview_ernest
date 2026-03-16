from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import FieldDoesNotExist
from back.models import Item, Group  # Previews
from django.db import models

User = get_user_model()

# Установка глобальных переводов для моделей
Item._meta.verbose_name = _('Prekė')
Item._meta.verbose_name_plural = _('Prekės')
Group._meta.verbose_name = _('Grupė')
Group._meta.verbose_name_plural = _('Grupės')
# Previews._meta.verbose_name = _('Peržiūra')
# Previews._meta.verbose_name_plural = _('Peržiūros')

# Установка переводов для полей моделей
MODEL_FIELD_TRANSLATIONS = {
    Item: {
        'length': _('Ilgis'),
        'width': _('Plotis'),
        'height': _('Aukštis'),
        'price': _('Kaina'),
        'name': _('Pavadinimas'),
        'related': _('Susiję'),
        'specification': _('Specifikacija'),
        'image': _('Paveikslėlis'),
        'position': _('Pozicija'),
    },
    Group: {
        'name': _('Pavadinimas'),
    },
    # Previews: {
    #     'name': _('Pavadinimas'),
    #     'image': _('Paveikslėlis'),
    # },
    User: {
        'show_prices': _('Rodyti kainas'),
        'show_sizes': _('Rodyti dydžius'),
        'show_logo_on_main_page': _('Rodyti logotipą pagrindiniame puslapyje'),
        'show_logo_on_preview': _('Rodyti logotipą peržiūros puslapyje'),
        'show_upper_button': _('Rodyti viršutinį mygtuką'),
        'show_lower_button': _('Rodyti apatinį mygtuką'),
        'show_lower_lower_button': _('Rodyti papildomą apatinį mygtuką'),
        'title_for_upper_button': _('Viršutinio mygtuko pavadinimas'),
        'title_for_lower_button': _('Apatinio mygtuko pavadinimas'),
        'title_for_lower_lower_button': _('Papildomo apatinio mygtuko pavadinimas'),
        'url_for_upper_button': _('Viršutinio mygtuko nuoroda'),
        'url_for_lower_button': _('Apatinio mygtuko nuoroda'),
        'url_for_lower_lower_button': _('Papildomo apatinio mygtuko nuoroda'),
        'url_for_search': _('Paieškos nuoroda'),
        'logo': _('Logotipas'),
    }
}

for model, fields in MODEL_FIELD_TRANSLATIONS.items():
    for field_name, translation in fields.items():
        try:
            field = model._meta.get_field(field_name)
            field.verbose_name = translation
        except FieldDoesNotExist:
            pass


class UserRestrictedAdmin(admin.ModelAdmin):
    user_field = 'user_for'

    def get_exclude(self, request, obj=None):
        if request.user.is_superuser:
            return None
        return (self.user_field,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(**{self.user_field: request.user})

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return True
        return getattr(obj, self.user_field) == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return True
        return getattr(obj, self.user_field) == request.user

    def save_model(self, request, obj, form, change):
        if not change or not getattr(obj, self.user_field):
            setattr(obj, self.user_field, request.user)
        super().save_model(request, obj, form, change)


@admin.register(Item)
class ItemAdmin(UserRestrictedAdmin):
    list_display = ('name', 'get_user', 'related', 'specification', 'position')
    list_filter = ('specification',)
    search_fields = ('name',)

    def get_user(self, obj):
        return obj.user_for.username

    get_user.short_description = 'Savininkas'
    get_user.admin_order_field = 'user_for__username'

    def get_form(self, request, obj=None, **kwargs):
        # Сохраняем объект в запросе для последующего использования
        request._obj = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Фильтрация категорий по пользователю
        if db_field.name == 'related':
            user = None
            
            # Определяем пользователя для фильтрации
            if hasattr(request, '_obj') and request._obj and request._obj.user_for:
                # Для существующего объекта используем его владельца
                user = request._obj.user_for
            elif request.method == 'POST':
                # При отправке формы используем выбранного пользователя
                user_id = request.POST.get('user_for')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        pass
            else:
                # Для новых объектов используем текущего пользователя
                user = request.user
            
            if user:
                kwargs["queryset"] = Group.objects.filter(user_for=user)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Устанавливаем user_for перед обработкой позиции
        if not change and not getattr(obj, self.user_field, None):
            setattr(obj, self.user_field, request.user)
            
        if not change:  # Новый объект
            self.handle_position_for_new_obj(obj)
        else:  # Существующий объект
            old_obj = Item.objects.get(pk=obj.pk)
            if (old_obj.position != obj.position or 
                old_obj.related != obj.related or 
                old_obj.specification != obj.specification):
                self.handle_position_for_existing_obj(old_obj, obj)
        
        # Вызываем родительский метод сохранения
        super().save_model(request, obj, form, change)

    def handle_position_for_new_obj(self, obj):
        """Обработка позиции для нового объекта"""
        # Находим элементы с позицией >= новой позиции
        conflict_items = Item.objects.filter(
            user_for=obj.user_for,
            related=obj.related,
            specification=obj.specification,
            position__gte=obj.position
        ).order_by('-position')
        
        # Сдвигаем конфликтные элементы на +1
        for item in conflict_items:
            item.position += 1
            item.save()

    def handle_position_for_existing_obj(self, old_obj, new_obj):
        if (old_obj.related == new_obj.related and 
            old_obj.specification == new_obj.specification):
            
            # Fixed: uses models.F
            Item.objects.filter(
                user_for=old_obj.user_for,
                related=old_obj.related,
                specification=old_obj.specification,
                position__gt=old_obj.position
            ).update(position=models.F('position') - 1)
            
            # Fixed: uses models.F
            Item.objects.filter(
                user_for=new_obj.user_for,
                related=new_obj.related,
                specification=new_obj.specification,
                position__gte=new_obj.position
            ).exclude(pk=new_obj.pk).update(position=models.F('position') + 1)
        
        # Случай 2: Изменилась группа или спецификация
        else:
            # Удаляем старую позицию в исходной группе
            Item.objects.filter(
                user_for=old_obj.user_for,
                related=old_obj.related,
                specification=old_obj.specification,
                position__gt=old_obj.position
            ).update(position=models.F('position') - 1)
            
            # Сдвигаем элементы в новой группе
            self.handle_position_for_new_obj(new_obj)


@admin.register(Group)
class GroupAdmin(UserRestrictedAdmin):
    list_display = ('name_lt', 'get_user')
    search_fields = ('name',)
    
    def name_lt(self, obj):
        return obj.name
    name_lt.short_description = _('Pavadinimas')

    def get_user(self, obj):
        return obj.user_for.username
    get_user.short_description = _('Savininkas')
    get_user.admin_order_field = 'user_for__username'


# @admin.register(Previews)
# class PreviewsAdmin(UserRestrictedAdmin):
#     list_display = ('name_lt', 'get_user', 'preview_image')
#     search_fields = ('name',)
    
#     def name_lt(self, obj):
#         return obj.name
#     name_lt.short_description = _('Pavadinimas')
#
#     def get_user(self, obj):
#         return obj.user_for.username
#     get_user.short_description = _('Savininkas')
#     get_user.admin_order_field = 'user_for__username'
#
#     def preview_image(self, obj):
#         if obj.image:
#             return f'<img src="{obj.image.url}" width="50" height="50" />'
#         return _("Nėra nuotraukos")
#     preview_image.short_description = _('Miniatiūra')
#     preview_image.allow_tags = True


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username_lt', 'email_lt', 'first_name_lt', 'last_name_lt', 'is_staff_lt', 'url_for_search_lt')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    def username_lt(self, obj):
        return obj.username
    username_lt.short_description = _('Vartotojo vardas')
    
    def email_lt(self, obj):
        return obj.email
    email_lt.short_description = _('El. paštas')
    
    def first_name_lt(self, obj):
        return obj.first_name
    first_name_lt.short_description = _('Vardas')
    
    def last_name_lt(self, obj):
        return obj.last_name
    last_name_lt.short_description = _('Pavardė')
    
    def is_staff_lt(self, obj):
        return _("Taip") if obj.is_staff else _("Ne")
    is_staff_lt.short_description = _('Personalo statusas')
    
    def url_for_search_lt(self, obj):
        return obj.url_for_search
    url_for_search_lt.short_description = _('Paieškos nuoroda')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Asmeninė informacija'), {'fields': ('first_name', 'last_name', 'email', 'logo')}),
        (_('Leidimai'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Svarbios datos'), {'fields': ('last_login', 'date_joined')}),
        (_('Platformos nustatymai'), {'fields': (
            'show_prices', 
            'show_sizes', 
            'show_logo_on_main_page',
            'show_logo_on_preview',
            'show_upper_button', 
            'show_lower_button',
            'show_lower_lower_button',
            'title_for_upper_button', 
            'title_for_lower_button', 
            'title_for_lower_lower_button',
            'url_for_upper_button',
            'url_for_lower_button',
            'url_for_lower_lower_button',
            'url_for_search'
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def __init__(self, model, admin_site):
        # Установка переводов для модели User
        model._meta.verbose_name = _('Vartotojas')
        model._meta.verbose_name_plural = _('Vartotojai')
        super().__init__(model, admin_site)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return self.fieldsets
        else:
            return (
                (None, {'fields': ('username',)}),
                (_('Asmeninė informacija'), {'fields': ('first_name', 'last_name', 'email', 'logo')}),
                (_('Platformos nustatymai'), {'fields': (
                    'show_prices', 
                    'show_sizes', 
                    'show_logo_on_main_page',
                    'show_logo_on_preview',
                    'show_upper_button', 
                    'show_lower_button',
                    'show_lower_lower_button',
                    'title_for_upper_button', 
                    'title_for_lower_button', 
                    'title_for_lower_lower_button',
                    'url_for_upper_button',
                    'url_for_lower_button',
                    'url_for_lower_lower_button',
                    'url_for_search'
                )}),
            )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return True
        return obj == request.user

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return [
                'username', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions',
                'last_login',
                'date_joined'
            ]
        return []