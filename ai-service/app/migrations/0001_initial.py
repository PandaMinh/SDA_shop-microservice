from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="InteractionEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("customer_id", models.IntegerField(db_index=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("search", "Search"),
                            ("view", "View"),
                            ("buy", "Buy"),
                            ("cart", "Cart"),
                            ("favorite", "Favorite"),
                        ],
                        max_length=20,
                    ),
                ),
                ("query", models.CharField(blank=True, default="", max_length=255)),
                ("product_id", models.IntegerField(blank=True, null=True)),
                ("product_type", models.CharField(blank=True, default="", max_length=20)),
                ("product_name", models.CharField(blank=True, default="", max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "interaction_events",
                "ordering": ["-created_at"],
            },
        ),
    ]
