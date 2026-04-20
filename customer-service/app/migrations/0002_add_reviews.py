from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="product_type",
            field=models.CharField(
                choices=[
                    ("mobile", "Mobile"),
                    ("desktop", "Desktop"),
                    ("clothes", "Clothes"),
                ],
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name="Review",
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
                ("product_id", models.IntegerField()),
                ("product_type", models.CharField(max_length=20)),
                ("rating", models.IntegerField()),
                ("comment", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "order",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="app.order",
                    ),
                ),
            ],
            options={
                "db_table": "order_reviews",
                "unique_together": {("order", "product_id", "product_type")},
            },
        ),
    ]
