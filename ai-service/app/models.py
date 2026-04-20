from django.db import models


class InteractionEvent(models.Model):
    EVENT_TYPES = [
        ("search", "Search"),
        ("view", "View"),
        ("click", "Click"),
        ("add_to_cart", "Add to Cart"),
        ("buy", "Buy"),
        ("cart", "Cart"),
        ("favorite", "Favorite"),
    ]

    customer_id = models.IntegerField(db_index=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    query = models.CharField(max_length=255, blank=True, default="")
    product_id = models.IntegerField(null=True, blank=True)
    product_type = models.CharField(max_length=20, blank=True, default="")
    product_name = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "interaction_events"
        ordering = ["-created_at"]

