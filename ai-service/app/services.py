from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import os
from datetime import timedelta
from typing import Any

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ModuleNotFoundError:  # pragma: no cover - dependency may be absent in local test env
    @dataclass(frozen=True)
    class HumanMessage:  # type: ignore[no-redef]
        content: str

    @dataclass(frozen=True)
    class SystemMessage:  # type: ignore[no-redef]
        content: str

    HumanMessage = Any  # type: ignore[assignment]
    SystemMessage = Any  # type: ignore[assignment]

from app.models import InteractionEvent


class RecommendationEngine:
    WEIGHTS = {
        "search": 1.0,
        "view": 2.0,
        "cart": 3.0,
        "favorite": 4.0,
        "buy": 5.0,
    }

    def score_products(
        self,
        customer_id: int,
        products: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        events = InteractionEvent.objects.filter(customer_id=customer_id)
        keyword_counter = Counter()
        product_scores: dict[int, float] = defaultdict(float)
        now = self._latest_event_time(events)
        for event in events:
            weight = self._time_weight(event, now) * self.WEIGHTS.get(event.event_type, 0.0)
            for token in self._tokens_from_event(event):
                keyword_counter[token] += weight
            if event.product_id is not None:
                product_scores[event.product_id] += weight

        for product in products:
            tokens = self._tokens_from_product(product)
            relevance = sum(keyword_counter[token] for token in tokens)
            popularity = product_scores.get(int(product["id"]), 0.0)
            stock_boost = 1.0 if int(product.get("stock", 0)) > 0 else -2.0
            product["score"] = round(relevance + popularity + stock_boost, 3)

        ranked = sorted(
            products,
            key=lambda item: (item.get("score", 0.0), int(item.get("stock", 0))),
            reverse=True,
        )
        return ranked[:8]

    def score_popular_products(self, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        popularity: dict[int, float] = defaultdict(float)
        events = InteractionEvent.objects.all()
        now = self._latest_event_time(events)
        for event in events:
            weight = self._time_weight(event, now) * self.WEIGHTS.get(event.event_type, 0.0)
            if event.product_id is not None:
                popularity[event.product_id] += weight

        for product in products:
            pid = int(product["id"])
            product["score"] = round(popularity.get(pid, 0.0) + float(product.get("stock", 0)), 3)

        return sorted(
            products,
            key=lambda item: (item.get("score", 0.0), int(item.get("stock", 0))),
            reverse=True,
        )[:8]

    def _latest_event_time(self, events: Any) -> Any:
        latest = None
        for event in events:
            if latest is None or event.created_at > latest:
                latest = event.created_at
        return latest

    def _time_weight(self, event: InteractionEvent, latest: Any) -> float:
        if latest is None:
            return 1.0
        age = latest - event.created_at
        if age <= timedelta(hours=6):
            return 1.3
        if age <= timedelta(days=2):
            return 1.1
        if age <= timedelta(days=7):
            return 1.0
        return 0.7

    def _tokens_from_event(self, event: InteractionEvent) -> list[str]:
        source = " ".join(
            [
                event.query,
                event.product_name,
                event.product_type,
                str(event.metadata.get("category", "")),
                str(event.metadata.get("brand", "")),
            ]
        )
        return self._tokenize(source)

    def _tokens_from_product(self, product: dict[str, Any]) -> list[str]:
        source = " ".join(
            [
                str(product.get("name", "")),
                str(product.get("brand", "")),
                str(product.get("category", "")),
                str(product.get("description", "")),
            ]
        )
        return self._tokenize(source)

    def _tokenize(self, text: str) -> list[str]:
        return [token for token in text.lower().replace("/", " ").split() if len(token) > 2]


class ChatRAGService:
    SYSTEM_PROMPT = (
        "You are a shopping assistant for an e-commerce store. "
        "Answer in Vietnamese. Use only the provided catalog context. "
        "If the catalog is insufficient, ask a short clarifying question. "
        "Prefer concise recommendations with product names, brands, and prices."
    )

    def __init__(self, llm: Any | None = None) -> None:
        api_key = os.environ.get("CEREBRAS_API_KEY") or os.environ.get("CEREBRES_API_KEY")
        self._llm = llm or self._build_llm(api_key)

    def _build_llm(self, api_key: str | None) -> Any:
        if api_key is None:
            return None
        try:
            from langchain_cerebras import ChatCerebras
        except ModuleNotFoundError:
            return None
        return ChatCerebras(
            model=os.environ.get("CEREBRAS_MODEL", "qwen-3-235b-a22b-instruct-2507"),
            api_key=api_key,
        )

    def build_response(
        self,
        message: str,
        customer_id: int | None,
        products: list[dict[str, Any]],
    ) -> dict[str, Any]:
        filters = self._extract_filters(message)
        matches = self._retrieve(message, products, filters)
        if not matches:
            return {
                "answer": self._fallback_answer(message),
                "sources": [],
            }

        top = matches[:6]
        context = self._format_context(top)
        answer = self._invoke_llm(message, context, filters)
        if not answer:
            answer = self._fallback_answer(message)
        return {
            "answer": answer,
            "sources": top,
        }

    def _invoke_llm(self, message: str, context: str, filters: dict[str, Any]) -> str:
        try:
            if self._llm is None:
                return ""
            prompt = self._build_messages(message, context, filters)
            response = self._llm.invoke(prompt)
            return str(response.content).strip()
        except Exception:
            return ""

    def _build_messages(self, message: str, context: str, filters: dict[str, Any]) -> list[Any]:
        return [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Catalog context:\n{context}\n\n"
                    f"Detected filters: {filters}\n\n"
                    f"User message: {message}"
                )
            ),
        ]

    def _format_context(self, products: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        for item in products:
            lines.append(
                " | ".join(
                    [
                        f"name={item.get('name')}",
                        f"brand={item.get('brand')}",
                        f"category={item.get('category')}",
                        f"price={item.get('price')}",
                        f"stock={item.get('stock')}",
                        f"description={item.get('description', '')}",
                        f"specs={item.get('specs', {})}",
                    ]
                )
            )
        return "\n".join(lines)

    def _fallback_answer(self, message: str) -> str:
        return (
            "Mình chưa tìm thấy sản phẩm phù hợp ngay lúc này. "
            "Bạn có thể nói rõ hơn về loại sản phẩm, hãng, hoặc mức giá mong muốn."
        )

    def _retrieve(
        self,
        message: str,
        products: list[dict[str, Any]],
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        query_tokens = set(self._tokenize(message))
        scored: list[tuple[float, dict[str, Any]]] = []
        for product in products:
            if not self._matches_filters(product, filters):
                continue
            tokens = set(
                self._tokenize(
                    " ".join(
                        [
                            str(product.get("name", "")),
                            str(product.get("brand", "")),
                            str(product.get("category", "")),
                            str(product.get("description", "")),
                            self._flatten_specs(product.get("specs", {})),
                        ]
                    )
                )
            )
            overlap = len(query_tokens & tokens)
            score = float(overlap)
            if product.get("stock", 0):
                score += 0.5
            if score > 0:
                scored.append((score, product))
        scored.sort(key=lambda item: item[0], reverse=True)
        ranked = [item[1] for item in scored]
        if ranked:
            return ranked
        fallback = [product for product in products if self._matches_filters(product, filters)]
        return sorted(fallback or products, key=lambda item: int(item.get("stock", 0)), reverse=True)

    def _extract_filters(self, message: str) -> dict[str, Any]:
        tokens = self._tokenize(message)
        category = None
        if "laptop" in tokens:
            category = "laptop"
        elif "pc" in tokens or "desktop" in tokens:
            category = "pc"
        elif "tablet" in tokens:
            category = "tablet"
        elif "phone" in tokens or "điện" in tokens or "dien" in tokens:
            category = "phone"
        elif "ao" in tokens or "áo" in message.lower():
            category = "ao"
        elif "quan" in tokens or "quần" in message.lower():
            category = "quan"

        brand = None
        brands = ("apple", "samsung", "dell", "hp", "lenovo", "asus", "acer", "msi", "nike", "adidas")
        for candidate in brands:
            if candidate in tokens:
                brand = candidate.title()
                break

        min_price, max_price = self._extract_price_range(message)
        return {"category": category, "brand": brand, "min_price": min_price, "max_price": max_price}

    def _extract_price_range(self, message: str) -> tuple[int | None, int | None]:
        text = message.lower().replace(".", "").replace(",", "")
        digits = [int(token) for token in text.split() if token.isdigit()]
        if "dưới" in text or "duoi" in text or "less than" in text:
            if digits:
                return None, self._scale_price_value(digits[0], text)
        if "từ" in text and "đến" in text:
            if len(digits) >= 2:
                return self._scale_price_value(digits[0], text), self._scale_price_value(digits[1], text)
        return None, None

    def _scale_price_value(self, value: int, text: str) -> int:
        if "triệu" in text or "trieu" in text:
            return value * 1_000_000
        if "nghìn" in text or "nghin" in text:
            return value * 1_000
        return value

    def _matches_filters(self, product: dict[str, Any], filters: dict[str, Any]) -> bool:
        category = filters.get("category")
        brand = filters.get("brand")
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        if category and str(product.get("category", "")).lower() != category.lower():
            return False
        if brand and brand.lower() not in str(product.get("brand", "")).lower():
            return False
        price = int(float(product.get("price", 0)))
        if min_price is not None and price < int(min_price):
            return False
        if max_price is not None and price > int(max_price):
            return False
        return True

    def _flatten_specs(self, specs: Any) -> str:
        if isinstance(specs, dict):
            return " ".join(f"{key} {value}" for key, value in specs.items())
        return str(specs)

    def _tokenize(self, text: str) -> list[str]:
        return [token for token in text.lower().replace(",", " ").split() if len(token) > 2]
