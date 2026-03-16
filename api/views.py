from django.http import JsonResponse
from rest_framework.generics import get_object_or_404
from back.models import Item, Group, ApiUser
#from group import user_for

'''
{
    "width": 120.5,
    "height": 80.0,
    "depth": 30.0,
    "unit": "cm"
}
'''

def components(request):
    type1 = request.GET.get('type', '')
    user = ApiUser.objects.first()
    specification = request.GET.get('specification', '')
    #print(get_object_or_404(Group, name=type1), specification)
    ans = [{
            'id': i[0],
            'name': i[1],
            'image_url': i[2],
            'price': i[3],
            'width': i[4],
            'height': i[5],
            'depth': i[6],
            } for i in Item.objects.all().filter(related=get_object_or_404(Group, user_for=user ,name=type1), specification=specification).order_by('position').values_list('id', 'name', 'image', 'price', 'width', 'height', 'length')]
    #print(ans)
    return JsonResponse(
        status=200,
        data=ans,
        safe=False
    )

def image(request):
    id1 = int(request.GET.get('id', ''))
    item = get_object_or_404(Item, pk=id1)
    return JsonResponse(
        status=200,
        data={'image_url': item.image.url[6:]},
    )
