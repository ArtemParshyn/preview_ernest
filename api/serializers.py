import rest_framework.serializers
from back.models import Item


class ItemSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'