from rest_framework import serializers
from .models import ClothesProduct, InventoryImport


class ClothesProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothesProduct
        fields = '__all__'


class InventoryImportSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InventoryImport
        fields = '__all__'
