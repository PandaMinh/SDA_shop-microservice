from rest_framework import serializers
from .models import DesktopProduct, InventoryImport


class DesktopProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesktopProduct
        fields = '__all__'


class InventoryImportSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InventoryImport
        fields = '__all__'
