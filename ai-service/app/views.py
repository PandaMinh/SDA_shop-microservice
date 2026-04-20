from __future__ import annotations

from typing import Any

import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from app.serializers import InteractionEventSerializer
from app.assignment import AssignmentPipelineService
from app.services import ChatRAGService, RecommendationEngine

REQUEST_TIMEOUT = 10


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok", "service": "ai-service"})


@api_view(["POST"])
def track_event(request):
    serializer = InteractionEventSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    event = serializer.save()
    return Response(InteractionEventSerializer(event).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def chat(request):
    message = str(request.data.get("message", "")).strip()
    if not message:
        return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

    customer_id = request.data.get("customer_id")
    products = _fetch_products()
    service = ChatRAGService()
    data = service.build_response(message, int(customer_id) if customer_id else None, products)
    return Response(data)


@api_view(["GET"])
def recommendations(request):
    customer_id = request.query_params.get("customer_id")
    query = str(request.query_params.get("query", "")).strip()
    signal = str(request.query_params.get("signal", "")).strip()

    products = _fetch_products()
    engine = RecommendationEngine()
    if customer_id:
        ranked = engine.score_products(int(customer_id), products, query=query, signal=signal)
        return Response({"customer_id": int(customer_id), "query": query, "signal": signal, "products": ranked})

    ranked = engine.score_popular_products(products)
    return Response({"customer_id": None, "query": query, "signal": signal, "products": ranked})


@api_view(["GET", "POST"])
def assignment_summary(request):
    products = _fetch_products()
    service = AssignmentPipelineService()
    summary = service.ensure_assets(products, force=(request.method == "POST"))
    return Response(summary)


def _fetch_products() -> list[dict[str, Any]]:
    try:
        response = requests.get(settings.PRODUCT_CATALOG_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        return list(payload.get("products", []))
    except requests.RequestException:
        return []
