from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from back.models import Group, Item, ApiUser, Previews
from preview import settings

def home(request):
    return render(request, 'home.html')

def done(request, id):
    user = get_object_or_404(ApiUser, url_for_search=id)
    previews = Previews.objects.filter(user_for=user)

    items = []
    for preview in previews:
        items.append({
            'name': preview.name,
            'image_url': request.build_absolute_uri(settings.MEDIA_URL + str(preview.image))
        })

    return render(request, 'done.html', {'items': items})

def index(request):
    user = ApiUser.objects.first()

    # Логотип
    try:
        logo = user.logo.url[7:]
    except Exception:
        logo = None

    def get_first_image(spec):
        item = Item.objects.filter(specification=spec, related__name = 'Didesnė', user_for=user).first()
        if item and item.image:
            return item.image.url[7:]
        return None

    photos = {
        'Plokstes': get_first_image('Plokstes'),
        'Takai': get_first_image('Takai'),
        'Sonai': get_first_image('Sonai'),
        'Paminklai': get_first_image('Paminklai'),
        'Priedai': get_first_image('Priedai'),
    }

    ans = {
        'show_prices': user.show_prices,
        'show_dimensions': user.show_sizes,
        'show_upper_button': user.show_upper_button,
        'show_lower_button': user.show_lower_button,
        'show_lower_lower_button': user.show_lower_lower_button,
        'show_logo_on_main_page': user.show_logo_on_main_page,
        'show_logo_on_preview': user.show_logo_on_preview,
        'title_for_upper_button': user.title_for_upper_button,
        'title_for_lower_button': user.title_for_lower_button,
        'title_for_lower_lower_button': user.title_for_lower_lower_button,
        'url_for_lower_lower_button': user.url_for_lower_lower_button,
        'url_for_upper_button': user.url_for_upper_button,
        'url_for_lower_button': user.url_for_lower_button,
        'items': [i[0] for i in Group.objects.filter(user_for=user).values_list('name')],
        'photos': photos,
        'logo': logo,
        'email': user.email,
    }
    return render(request, 'index.html', context=ans)


def notfound(request):
    return render(request, 'notfound.html')

'''
('Paminklai', 'Paminklai'),
        ('', 'Sonai'),
        ('', 'Takai'),
        ('', 'Plokstes')




<button id="id_for_but"
                        class="px-5 py-2 rounded-2xl font-semibold shadow transition-colors duration-200 bg-blue-600 text-white"
                        data-type="Didesnė">Didesnė</button>
'''