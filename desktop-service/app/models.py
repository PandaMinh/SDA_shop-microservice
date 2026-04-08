from django.db import models


class DesktopProduct(models.Model):
    CATEGORY_CHOICES = [
        ('laptop', 'Laptop'),
        ('pc', 'PC'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    specs = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'desktop_products'

    def __str__(self):
        return self.name


class InventoryImport(models.Model):
    product = models.ForeignKey(DesktopProduct, on_delete=models.CASCADE, related_name='imports')
    quantity_imported = models.IntegerField()
    cost_price = models.DecimalField(max_digits=14, decimal_places=2)
    supplier = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    imported_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'desktop_inventory_imports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Nhập {self.quantity_imported} x {self.product.name}"
