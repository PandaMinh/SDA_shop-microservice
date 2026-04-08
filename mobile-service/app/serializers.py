from rest_framework import serializers
from .models import MobileProduct, InventoryImport


class MobileProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileProduct
        fields = '__all__'


class InventoryImportSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InventoryImport
        fields = '__all__'
