from rest_framework import serializers

from app.models import InteractionEvent


class InteractionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionEvent
        fields = "__all__"

