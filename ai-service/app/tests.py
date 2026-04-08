from django.test import TestCase
from django.utils import timezone

from app.models import InteractionEvent
from app.services import ChatRAGService, RecommendationEngine


class RecommendationEngineTests(TestCase):
    def test_score_products_prefers_products_matching_events(self):
        InteractionEvent.objects.create(
            customer_id=1,
            event_type="search",
            query="iphone 15 pro",
            product_name="iPhone 15 Pro",
            metadata={"brand": "Apple", "category": "phone"},
        )
        products = [
            {"id": 1, "name": "iPhone 15 Pro", "brand": "Apple", "category": "phone", "stock": 5},
            {"id": 2, "name": "Dell XPS", "brand": "Dell", "category": "laptop", "stock": 9},
        ]
        ranked = RecommendationEngine().score_products(1, products)
        self.assertEqual(ranked[0]["id"], 1)


class ChatRAGServiceTests(TestCase):
    def test_build_response_returns_sources_for_matching_query(self):
        products = [
            {
                "id": 1,
                "name": "MacBook Air M3",
                "brand": "Apple",
                "category": "laptop",
                "price": "31990000",
                "stock": 7,
                "description": "M3 chip",
                "specs": {"ram": "16GB"},
            },
            {
                "id": 2,
                "name": "Galaxy S24",
                "brand": "Samsung",
                "category": "phone",
                "price": "22990000",
                "stock": 3,
                "description": "AI phone",
                "specs": {"ram": "12GB"},
            },
        ]
        service = ChatRAGService(llm=_FakeLLM("Tôi gợi ý MacBook Air M3 cho bạn."))
        data = service.build_response("Tôi muốn mua macbook", None, products)
        self.assertTrue(data["sources"])

    def test_build_response_includes_catalog_context_in_prompt(self):
        products = [
            {
                "id": 1,
                "name": "MacBook Air M3",
                "brand": "Apple",
                "category": "laptop",
                "price": "31990000",
                "stock": 7,
                "description": "M3 chip",
                "specs": {"ram": "16GB"},
            }
        ]
        llm = _PromptCaptureLLM()
        ChatRAGService(llm=llm).build_response("macbook", None, products)
        self.assertIn("Catalog context:", llm.prompt_text)
        self.assertIn("MacBook Air M3", llm.prompt_text)
        self.assertIn("specs", llm.prompt_text)

    def test_build_response_filters_catalog_by_category_and_price(self):
        products = [
            {
                "id": 1,
                "name": "MacBook Air M3",
                "brand": "Apple",
                "category": "laptop",
                "price": "31990000",
                "stock": 7,
                "description": "M3 chip",
                "specs": {"ram": "16GB"},
            },
            {
                "id": 2,
                "name": "Galaxy S24",
                "brand": "Samsung",
                "category": "phone",
                "price": "22990000",
                "stock": 3,
                "description": "AI phone",
                "specs": {"ram": "12GB"},
            },
        ]
        llm = _PromptCaptureLLM()
        data = ChatRAGService(llm=llm).build_response("tìm laptop dưới 30 triệu", None, products)
        self.assertEqual(data["sources"][0]["id"], 1)


class _FakeLLM:
    def __init__(self, text: str) -> None:
        self.text = text

    def invoke(self, messages):  # type: ignore[no-untyped-def]
        class _Message:
            def __init__(self, content: str) -> None:
                self.content = content

        return _Message(self.text)


class _PromptCaptureLLM:
    def __init__(self) -> None:
        self.prompt_text = ""

    def invoke(self, messages):  # type: ignore[no-untyped-def]
        self.prompt_text = "\n".join(getattr(message, "content", "") for message in messages)

        class _Message:
            content = "ok"

        return _Message()


class RecommendationEngineRecencyTests(TestCase):
    def test_score_products_prefers_recent_events(self):
        older = InteractionEvent.objects.create(
            customer_id=1,
            event_type="view",
            product_id=1,
            product_name="MacBook Air M3",
            metadata={"brand": "Apple", "category": "laptop"},
        )
        newer = InteractionEvent.objects.create(
            customer_id=1,
            event_type="view",
            product_id=2,
            product_name="Galaxy S24",
            metadata={"brand": "Samsung", "category": "phone"},
        )
        old_time = timezone.now() - timezone.timedelta(days=10)
        new_time = timezone.now()
        InteractionEvent.objects.filter(pk=older.pk).update(created_at=old_time)
        InteractionEvent.objects.filter(pk=newer.pk).update(created_at=new_time)
        products = [
            {"id": 1, "name": "MacBook Air M3", "brand": "Apple", "category": "laptop", "stock": 1},
            {"id": 2, "name": "Galaxy S24", "brand": "Samsung", "category": "phone", "stock": 1},
        ]
        ranked = RecommendationEngine().score_products(1, products)
        self.assertEqual(ranked[0]["id"], 2)
