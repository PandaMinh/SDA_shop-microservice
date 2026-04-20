from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "ai-service-secret-key-change-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "corsheaders",
    "app",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOW_ALL_ORIGINS = True
APPEND_SLASH = False
REST_FRAMEWORK = {"DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"]}
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True

PRODUCT_CATALOG_URL = os.environ.get("PRODUCT_CATALOG_URL", "http://api-gateway:8000/api/products")
CEREBRAS_MODEL = "qwen-3-235b-a22b-instruct-2507"
CEREBRAS_API_KEY_ENV = "CEREBRAS_API_KEY"
AI_ARTIFACTS_DIR = BASE_DIR / "artifacts"
AI_DATASET_PATH = AI_ARTIFACTS_DIR / "data_user500.csv"
AI_MODEL_REPORT_PATH = AI_ARTIFACTS_DIR / "reports" / "model_report.json"
AI_MODEL_BUNDLE_PATH = AI_ARTIFACTS_DIR / "reports" / "model_bundle.json"
AI_GRAPH_PATH = AI_ARTIFACTS_DIR / "reports" / "kb_graph.json"
AI_GRAPH_CYPHER_PATH = AI_ARTIFACTS_DIR / "reports" / "kb_graph.cypher"
NEO4J_URI = os.environ.get("NEO4J_URI", "")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")
