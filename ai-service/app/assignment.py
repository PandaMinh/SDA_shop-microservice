from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from django.conf import settings


ACTIONS = ("view", "click", "add_to_cart")
ACTION_INDEX = {action: index for index, action in enumerate(ACTIONS)}


def _utc_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat()


def _safe_slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-") or "item"


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(settings.BASE_DIR))
    except ValueError:
        return str(path)


def _default_products() -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    seeds = [
        ("phone", "Apple", "iPhone 15"),
        ("phone", "Samsung", "Galaxy S24"),
        ("tablet", "Apple", "iPad Air"),
        ("tablet", "Samsung", "Galaxy Tab S9"),
        ("laptop", "Dell", "XPS"),
        ("laptop", "Asus", "ROG Zephyrus"),
        ("pc", "HP", "Victus Desktop"),
        ("pc", "Lenovo", "Legion Tower"),
        ("shirt", "Nike", "Tech Tee"),
        ("pants", "Adidas", "Runner Pants"),
    ]
    for index, (category, brand, name) in enumerate(seeds, start=1):
        for variant in range(1, 4):
            catalog.append(
                {
                    "id": index * 100 + variant,
                    "name": f"{name} {variant}",
                    "brand": brand,
                    "category": category,
                    "price": str(2_000_000 * index + variant * 350_000),
                    "stock": 3 + ((index + variant) % 8),
                    "description": f"{brand} {category} phien ban {variant}",
                    "type": "clothes" if category in {"shirt", "pants"} else ("mobile" if category in {"phone", "tablet"} else "desktop"),
                }
            )
    return catalog


def _macro_metrics(matrix: list[list[int]]) -> dict[str, float]:
    total = sum(sum(row) for row in matrix)
    correct = sum(matrix[i][i] for i in range(len(matrix)))
    precision_scores: list[float] = []
    recall_scores: list[float] = []
    f1_scores: list[float] = []
    for idx in range(len(matrix)):
        tp = matrix[idx][idx]
        fp = sum(matrix[row][idx] for row in range(len(matrix)) if row != idx)
        fn = sum(matrix[idx][col] for col in range(len(matrix)) if col != idx)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        precision_scores.append(precision)
        recall_scores.append(recall)
        f1_scores.append(f1)
    return {
        "accuracy": round(correct / total, 4) if total else 0.0,
        "precision_macro": round(sum(precision_scores) / len(precision_scores), 4),
        "recall_macro": round(sum(recall_scores) / len(recall_scores), 4),
        "f1_macro": round(sum(f1_scores) / len(f1_scores), 4),
        "support": total,
    }


def _line_chart_svg(title: str, history: list[dict[str, float]]) -> str:
    width = 760
    height = 320
    left = 70
    bottom = 250
    chart_width = 620
    chart_height = 170
    epochs = [item["epoch"] for item in history]
    accuracy = [item["accuracy"] for item in history]
    f1_scores = [item["f1_macro"] for item in history]

    def points(values: list[float]) -> str:
        if len(values) == 1:
            x = left + chart_width / 2
            y = bottom - values[0] * chart_height
            return f"{x:.2f},{y:.2f}"
        coords = []
        for index, value in enumerate(values):
            x = left + index * (chart_width / (len(values) - 1))
            y = bottom - value * chart_height
            coords.append(f"{x:.2f},{y:.2f}")
        return " ".join(coords)

    epoch_labels = "".join(
        f'<text x="{left + (idx * (chart_width / max(len(epochs) - 1, 1))):.2f}" y="{bottom + 24}" '
        f'font-size="12" text-anchor="middle" fill="#475569">E{epoch}</text>'
        for idx, epoch in enumerate(epochs)
    )
    y_labels = "".join(
        f'<text x="{left - 18}" y="{bottom - step * chart_height / 4 + 4:.2f}" font-size="11" '
        f'text-anchor="end" fill="#475569">{step / 4:.2f}</text>'
        for step in range(5)
    )
    grid = "".join(
        f'<line x1="{left}" y1="{bottom - step * chart_height / 4:.2f}" x2="{left + chart_width}" '
        f'y2="{bottom - step * chart_height / 4:.2f}" stroke="#dbeafe" stroke-width="1" />'
        for step in range(5)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="#ffffff" rx="18" />
<text x="40" y="36" font-size="22" font-weight="700" fill="#0f172a">{title}</text>
<text x="40" y="60" font-size="13" fill="#475569">Theo doi Accuracy va F1-macro qua 6 epoch</text>
{grid}
<line x1="{left}" y1="{bottom}" x2="{left + chart_width}" y2="{bottom}" stroke="#94a3b8" stroke-width="1.5" />
<line x1="{left}" y1="{bottom}" x2="{left}" y2="{bottom - chart_height}" stroke="#94a3b8" stroke-width="1.5" />
{epoch_labels}
{y_labels}
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="{points(accuracy)}" />
<polyline fill="none" stroke="#f97316" stroke-width="3" points="{points(f1_scores)}" />
<circle cx="{left + chart_width - 130}" cy="84" r="6" fill="#2563eb" />
<text x="{left + chart_width - 115}" y="88" font-size="12" fill="#1e293b">Accuracy</text>
<circle cx="{left + chart_width - 130}" cy="108" r="6" fill="#f97316" />
<text x="{left + chart_width - 115}" y="112" font-size="12" fill="#1e293b">F1-macro</text>
</svg>"""


def _comparison_chart_svg(results: list[dict[str, Any]]) -> str:
    width = 760
    height = 360
    bar_width = 110
    spacing = 90
    base_y = 290
    origin_x = 120
    colors = ["#2563eb", "#0f766e", "#7c3aed"]
    bars = []
    labels = []
    for index, result in enumerate(results):
        value = float(result["metrics"]["f1_macro"])
        height_px = value * 180
        x = origin_x + index * (bar_width + spacing)
        y = base_y - height_px
        bars.append(
            f'<rect x="{x}" y="{y:.2f}" width="{bar_width}" height="{height_px:.2f}" rx="16" fill="{colors[index % len(colors)]}" />'
            f'<text x="{x + bar_width / 2}" y="{y - 10:.2f}" font-size="14" text-anchor="middle" fill="#0f172a">{value:.3f}</text>'
        )
        labels.append(
            f'<text x="{x + bar_width / 2}" y="{base_y + 28}" font-size="13" text-anchor="middle" fill="#334155">{result["name"]}</text>'
        )
    grid = "".join(
        f'<line x1="90" y1="{base_y - step * 45}" x2="670" y2="{base_y - step * 45}" stroke="#e2e8f0" stroke-width="1" />'
        for step in range(5)
    )
    y_labels = "".join(
        f'<text x="80" y="{base_y - step * 45 + 4}" font-size="11" text-anchor="end" fill="#64748b">{step * 0.25:.2f}</text>'
        for step in range(5)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="#ffffff" rx="18" />
<text x="40" y="36" font-size="22" font-weight="700" fill="#0f172a">So sanh 3 mo hinh sequence</text>
<text x="40" y="60" font-size="13" fill="#475569">Gia tri cot la F1-macro tren tap test</text>
{grid}
{y_labels}
<line x1="90" y1="{base_y}" x2="670" y2="{base_y}" stroke="#94a3b8" stroke-width="1.5" />
{"".join(bars)}
{"".join(labels)}
</svg>"""


def _confusion_svg(title: str, matrix: list[list[int]]) -> str:
    width = 520
    height = 420
    start_x = 150
    start_y = 120
    cell = 80
    maximum = max(max(row) for row in matrix) or 1
    rects: list[str] = []
    labels: list[str] = []
    for row_idx, action_row in enumerate(ACTIONS):
        labels.append(
            f'<text x="120" y="{start_y + row_idx * cell + cell / 2 + 5:.2f}" text-anchor="end" font-size="13" fill="#334155">{action_row}</text>'
        )
        labels.append(
            f'<text x="{start_x + row_idx * cell + cell / 2:.2f}" y="100" text-anchor="middle" font-size="13" fill="#334155">{action_row}</text>'
        )
        for col_idx, value in enumerate(matrix[row_idx]):
            shade = 245 - math.floor((value / maximum) * 110)
            color = f"rgb(30,{shade},{255 - (maximum - value) % 40})"
            x = start_x + col_idx * cell
            y = start_y + row_idx * cell
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}" stroke="#ffffff" stroke-width="3" rx="10" />'
                f'<text x="{x + cell / 2}" y="{y + cell / 2 + 5}" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">{value}</text>'
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="#ffffff" rx="18" />
<text x="40" y="36" font-size="22" font-weight="700" fill="#0f172a">{title}</text>
<text x="40" y="62" font-size="13" fill="#475569">Hang = nhan that, cot = nhan du doan</text>
<text x="70" y="92" font-size="12" fill="#64748b">True label</text>
<text x="{start_x + 60}" y="76" font-size="12" fill="#64748b">Predicted label</text>
{"".join(labels)}
{"".join(rects)}
</svg>"""


@dataclass
class SequenceExample:
    current_category: str
    current_brand: str
    history_actions: list[str]
    history_categories: list[str]
    target_action: str
    next_action: str | None = None


class BaseSequenceModel:
    name = "BASE"

    def __init__(self) -> None:
        self.counts: dict[str, Counter[str]] = defaultdict(Counter)
        self.global_counts: Counter[str] = Counter()

    def training_keys(self, example: SequenceExample) -> list[str]:
        raise NotImplementedError

    def prediction_keys(self, example: SequenceExample) -> list[tuple[str, float]]:
        raise NotImplementedError

    def fit(self, examples: list[SequenceExample]) -> None:
        self.counts = defaultdict(Counter)
        self.global_counts = Counter()
        for example in examples:
            for key in self.training_keys(example):
                self.counts[key][example.target_action] += 1
            self.global_counts[example.target_action] += 1

    def probabilities(self, example: SequenceExample) -> dict[str, float]:
        scores = {action: 1.0 for action in ACTIONS}
        for key, weight in self.prediction_keys(example):
            bucket = self.counts.get(key)
            if not bucket:
                continue
            total = sum(bucket.values()) + len(ACTIONS)
            for action in ACTIONS:
                scores[action] += weight * ((bucket.get(action, 0) + 1) / total)
        total_scores = sum(scores.values())
        return {action: scores[action] / total_scores for action in ACTIONS}

    def predict(self, example: SequenceExample) -> str:
        probabilities = self.probabilities(example)
        return max(probabilities.items(), key=lambda item: item[1])[0]

    def score_add_to_cart(self, history_actions: list[str], history_categories: list[str], category: str, brand: str) -> float:
        example = SequenceExample(
            current_category=category,
            current_brand=brand,
            history_actions=history_actions[-3:],
            history_categories=history_categories[-3:],
            target_action="view",
            next_action=None,
        )
        return round(self.probabilities(example)["add_to_cart"], 4)

    def dump(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "counts": {key: dict(value) for key, value in self.counts.items()},
            "global_counts": dict(self.global_counts),
        }

    def load(self, payload: dict[str, Any]) -> "BaseSequenceModel":
        self.counts = defaultdict(Counter, {key: Counter(value) for key, value in payload.get("counts", {}).items()})
        self.global_counts = Counter(payload.get("global_counts", {}))
        return self


class RNNSequenceModel(BaseSequenceModel):
    name = "RNN"

    def training_keys(self, example: SequenceExample) -> list[str]:
        last_action = example.history_actions[-1] if example.history_actions else "start"
        return [
            f"rnn:last={last_action}|cat={example.current_category}",
            f"rnn:cat={example.current_category}",
            f"rnn:brand={example.current_brand}",
        ]

    def prediction_keys(self, example: SequenceExample) -> list[tuple[str, float]]:
        last_action = example.history_actions[-1] if example.history_actions else "start"
        return [
            (f"rnn:last={last_action}|cat={example.current_category}", 1.3),
            (f"rnn:cat={example.current_category}", 0.8),
            (f"rnn:brand={example.current_brand}", 0.5),
        ]


class LSTMSequenceModel(BaseSequenceModel):
    name = "LSTM"

    def training_keys(self, example: SequenceExample) -> list[str]:
        h3 = ",".join(example.history_actions[-3:]) or "start"
        h2 = ",".join(example.history_actions[-2:]) or "start"
        preferred_category = example.history_categories[-1] if example.history_categories else "unknown"
        return [
            f"lstm:h3={h3}|cat={example.current_category}|pref={preferred_category}",
            f"lstm:h2={h2}|cat={example.current_category}",
            f"lstm:pref={preferred_category}|brand={example.current_brand}",
            f"lstm:cat={example.current_category}",
        ]

    def prediction_keys(self, example: SequenceExample) -> list[tuple[str, float]]:
        h3 = ",".join(example.history_actions[-3:]) or "start"
        h2 = ",".join(example.history_actions[-2:]) or "start"
        preferred_category = example.history_categories[-1] if example.history_categories else "unknown"
        return [
            (f"lstm:h3={h3}|cat={example.current_category}|pref={preferred_category}", 1.8),
            (f"lstm:h2={h2}|cat={example.current_category}", 1.2),
            (f"lstm:pref={preferred_category}|brand={example.current_brand}", 0.8),
            (f"lstm:cat={example.current_category}", 0.5),
        ]


class BiLSTMSequenceModel(LSTMSequenceModel):
    name = "BiLSTM"

    def training_keys(self, example: SequenceExample) -> list[str]:
        keys = super().training_keys(example)
        prev_action = example.history_actions[-1] if example.history_actions else "start"
        next_action = example.next_action or "end"
        keys.append(f"bilstm:prev={prev_action}|next={next_action}|cat={example.current_category}")
        return keys

    def prediction_keys(self, example: SequenceExample) -> list[tuple[str, float]]:
        keys = list(super().prediction_keys(example))
        prev_action = example.history_actions[-1] if example.history_actions else "start"
        next_action = example.next_action or "unknown"
        keys.insert(0, (f"bilstm:prev={prev_action}|next={next_action}|cat={example.current_category}", 2.0))
        return keys


MODEL_TYPES: dict[str, type[BaseSequenceModel]] = {
    "RNN": RNNSequenceModel,
    "LSTM": LSTMSequenceModel,
    "BiLSTM": BiLSTMSequenceModel,
}


class AssignmentPipelineService:
    def __init__(self) -> None:
        self.artifacts_dir = Path(getattr(settings, "AI_ARTIFACTS_DIR", Path(settings.BASE_DIR) / "artifacts"))
        self.dataset_path = Path(getattr(settings, "AI_DATASET_PATH", self.artifacts_dir / "data_user500.csv"))
        self.reports_dir = self.artifacts_dir / "reports"
        self.plots_dir = self.reports_dir / "plots"
        self.model_report_path = Path(getattr(settings, "AI_MODEL_REPORT_PATH", self.reports_dir / "model_report.json"))
        self.graph_path = Path(getattr(settings, "AI_GRAPH_PATH", self.reports_dir / "kb_graph.json"))
        self.cypher_path = Path(getattr(settings, "AI_GRAPH_CYPHER_PATH", self.reports_dir / "kb_graph.cypher"))
        self.bundle_path = Path(getattr(settings, "AI_MODEL_BUNDLE_PATH", self.reports_dir / "model_bundle.json"))
        self.summary_path = self.reports_dir / "assignment_summary.json"
        self.neo4j_uri = getattr(settings, "NEO4J_URI", "")
        self.neo4j_user = getattr(settings, "NEO4J_USER", "neo4j")
        self.neo4j_password = getattr(settings, "NEO4J_PASSWORD", "password")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def ensure_assets(self, products: list[dict[str, Any]] | None = None, force: bool = False) -> dict[str, Any]:
        catalog = self._catalog(products)
        if force or not self.dataset_path.exists():
            self.generate_dataset(catalog)
        rows = self.load_dataset()
        if force or not self.model_report_path.exists() or not self.bundle_path.exists():
            self.train_models(rows, catalog)
        if force or not self.graph_path.exists() or not self.cypher_path.exists():
            self.build_graph(rows, catalog)
        summary = self._build_summary(rows, catalog)
        self.summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return summary

    def _catalog(self, products: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        if products:
            normalized: list[dict[str, Any]] = []
            for item in products:
                normalized.append(
                    {
                        "id": int(item["id"]),
                        "name": str(item.get("name", "")),
                        "brand": str(item.get("brand", "Unknown")),
                        "category": str(item.get("category", "unknown")),
                        "price": str(item.get("price", "0")),
                        "stock": int(float(item.get("stock", 0))),
                        "description": str(item.get("description", "")),
                        "type": str(item.get("type", "desktop")),
                    }
                )
            if normalized:
                return normalized
        return _default_products()

    def generate_dataset(self, catalog: list[dict[str, Any]]) -> None:
        rng = random.Random(42)
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in catalog:
            grouped[item["category"]].append(item)
        personas = [
            {"categories": ["phone", "tablet"], "brand": ["Apple", "Samsung"], "flow": ["view", "click", "view", "click", "add_to_cart"]},
            {"categories": ["laptop", "pc"], "brand": ["Dell", "Asus", "Lenovo", "HP"], "flow": ["view", "view", "click", "click", "add_to_cart"]},
            {"categories": ["shirt", "pants"], "brand": ["Nike", "Adidas"], "flow": ["view", "click", "view", "add_to_cart"]},
        ]
        rows: list[dict[str, Any]] = []
        base = datetime(2026, 4, 1, 8, 0, 0)
        for user_id in range(1, 501):
            persona = personas[(user_id - 1) % len(personas)]
            current = base + timedelta(minutes=user_id * 7)
            preferred_category = persona["categories"][rng.randrange(len(persona["categories"]))]
            behavior_count = 8
            for step in range(behavior_count):
                category_pool = persona["categories"] if rng.random() < 0.78 else list(grouped.keys())
                category = category_pool[rng.randrange(len(category_pool))]
                product = rng.choice(grouped.get(category) or catalog)
                flow = persona["flow"]
                action = flow[min(step, len(flow) - 1)]
                if action == "add_to_cart" and step < 2:
                    action = "click"
                if category != preferred_category and action == "add_to_cart" and rng.random() < 0.6:
                    action = "click"
                current += timedelta(minutes=rng.randint(5, 180))
                rows.append(
                    {
                        "user_id": user_id,
                        "product_id": int(product["id"]),
                        "action": action,
                        "timestamp": _utc_iso(current),
                    }
                )
        with self.dataset_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["user_id", "product_id", "action", "timestamp"])
            writer.writeheader()
            writer.writerows(rows)

    def load_dataset(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        with self.dataset_path.open("r", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                rows.append(
                    {
                        "user_id": int(row["user_id"]),
                        "product_id": int(row["product_id"]),
                        "action": str(row["action"]),
                        "timestamp": str(row["timestamp"]),
                    }
                )
        rows.sort(key=lambda item: (item["user_id"], item["timestamp"]))
        return rows

    def _examples(self, rows: list[dict[str, Any]], catalog: list[dict[str, Any]]) -> list[SequenceExample]:
        product_index = {int(item["id"]): item for item in catalog}
        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[int(row["user_id"])].append(row)
        examples: list[SequenceExample] = []
        for _, events in grouped.items():
            history_actions: list[str] = []
            history_categories: list[str] = []
            for idx, event in enumerate(events):
                product = product_index.get(int(event["product_id"]), {})
                next_action = events[idx + 1]["action"] if idx + 1 < len(events) else None
                examples.append(
                    SequenceExample(
                        current_category=str(product.get("category", "unknown")),
                        current_brand=str(product.get("brand", "Unknown")),
                        history_actions=history_actions[-3:],
                        history_categories=history_categories[-3:],
                        target_action=str(event["action"]),
                        next_action=next_action,
                    )
                )
                history_actions.append(str(event["action"]))
                history_categories.append(str(product.get("category", "unknown")))
        return examples

    def train_models(self, rows: list[dict[str, Any]], catalog: list[dict[str, Any]]) -> dict[str, Any]:
        examples = self._examples(rows, catalog)
        split_user = 400
        train_examples = [example for row, example in zip(rows, examples) if int(row["user_id"]) <= split_user]
        test_examples = [example for row, example in zip(rows, examples) if int(row["user_id"]) > split_user]
        results: list[dict[str, Any]] = []
        bundles: dict[str, Any] = {}
        for name, model_cls in MODEL_TYPES.items():
            history: list[dict[str, float]] = []
            for epoch in range(1, 7):
                cutoff = max(1, int(len(train_examples) * epoch / 6))
                probe_model = model_cls()
                probe_model.fit(train_examples[:cutoff])
                metrics, _ = self._evaluate_model(probe_model, test_examples)
                history.append({"epoch": epoch, "accuracy": metrics["accuracy"], "f1_macro": metrics["f1_macro"]})
            final_model = model_cls()
            final_model.fit(train_examples)
            metrics, confusion = self._evaluate_model(final_model, test_examples)
            plot_path = self.plots_dir / f"{_safe_slug(name)}_history.svg"
            plot_path.write_text(_line_chart_svg(f"Lich su hoc tap {name}", history), encoding="utf-8")
            confusion_path = self.plots_dir / f"{_safe_slug(name)}_confusion.svg"
            confusion_path.write_text(_confusion_svg(f"Confusion Matrix {name}", confusion), encoding="utf-8")
            results.append(
                {
                    "name": name,
                    "metrics": metrics,
                    "history": history,
                    "confusion_matrix": confusion,
                    "plots": {
                        "history": _relative(plot_path),
                        "confusion": _relative(confusion_path),
                    },
                }
            )
            bundles[name] = final_model.dump()
        comparison_path = self.plots_dir / "model_comparison.svg"
        comparison_path.write_text(_comparison_chart_svg(results), encoding="utf-8")
        best = max(results, key=lambda item: (item["metrics"]["f1_macro"], item["metrics"]["accuracy"]))
        report = {
            "dataset": {
                "rows": len(rows),
                "train_rows": len(train_examples),
                "test_rows": len(test_examples),
            },
            "models": results,
            "best_model": best["name"],
            "comparison_plot": _relative(comparison_path),
            "evaluation_note": (
                f"Mo hinh {best['name']} dat F1-macro {best['metrics']['f1_macro']:.3f}, "
                f"cao nhat tren tap test nen duoc chon lam model_best."
            ),
        }
        self.model_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        self.bundle_path.write_text(json.dumps({"best_model": best["name"], "models": bundles}, indent=2), encoding="utf-8")
        return report

    def _evaluate_model(self, model: BaseSequenceModel, examples: list[SequenceExample]) -> tuple[dict[str, float], list[list[int]]]:
        confusion = [[0 for _ in ACTIONS] for _ in ACTIONS]
        for example in examples:
            predicted = model.predict(example)
            confusion[ACTION_INDEX[example.target_action]][ACTION_INDEX[predicted]] += 1
        return _macro_metrics(confusion), confusion

    def load_model_report(self) -> dict[str, Any]:
        if not self.model_report_path.exists():
            self.ensure_assets()
        return json.loads(self.model_report_path.read_text(encoding="utf-8"))

    def load_summary(self) -> dict[str, Any]:
        if not self.summary_path.exists():
            self.ensure_assets()
        return json.loads(self.summary_path.read_text(encoding="utf-8"))

    def build_graph(self, rows: list[dict[str, Any]], catalog: list[dict[str, Any]]) -> dict[str, Any]:
        product_index = {int(item["id"]): item for item in catalog}
        nodes: dict[str, dict[str, Any]] = {}
        edge_map: dict[tuple[str, str, str], dict[str, Any]] = {}

        def add_node(node_id: str, label: str, **properties: Any) -> None:
            nodes[node_id] = {"id": node_id, "label": label, "properties": properties}

        def add_edge(source: str, target: str, relation: str, **properties: Any) -> None:
            key = (source, target, relation)
            if key not in edge_map:
                edge_map[key] = {"source": source, "target": target, "relation": relation, "properties": {"weight": 0}}
            edge_map[key]["properties"]["weight"] += int(properties.get("weight", 1))
            for name, value in properties.items():
                if name == "weight":
                    continue
                edge_map[key]["properties"][name] = value

        for action in ACTIONS:
            add_node(f"action:{action}", "Action", name=action)
        for product in catalog:
            pid = int(product["id"])
            add_node(f"product:{pid}", "Product", name=product["name"], category=product["category"], brand=product["brand"])
            add_node(f"category:{product['category']}", "Category", name=product["category"])
            add_node(f"brand:{product['brand']}", "Brand", name=product["brand"])
            add_edge(f"product:{pid}", f"category:{product['category']}", "IN_CATEGORY")
            add_edge(f"product:{pid}", f"brand:{product['brand']}", "OF_BRAND")

        for row in rows:
            user_node = f"user:{row['user_id']}"
            product = product_index.get(int(row["product_id"]), {})
            add_node(user_node, "User", user_id=row["user_id"])
            add_edge(user_node, f"product:{row['product_id']}", row["action"], weight=1)
            add_edge(user_node, f"action:{row['action']}", "PERFORMED", weight=1)
            if product:
                add_edge(user_node, f"category:{product['category']}", "INTERESTED_IN", weight=1)
                add_edge(user_node, f"brand:{product['brand']}", "LIKES_BRAND", weight=1)

        graph = {
            "nodes": list(nodes.values()),
            "edges": list(edge_map.values()),
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edge_map),
                "rows": len(rows),
            },
        }
        self.graph_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
        cypher_lines: list[str] = []
        for node in graph["nodes"]:
            properties = ", ".join(f"{key}: {json.dumps(value)}" for key, value in node["properties"].items())
            cypher_lines.append(f"MERGE (n:{node['label']} {{id: {json.dumps(node['id'])}}}) SET n += {{{properties}}};")
        for edge in graph["edges"]:
            props = ", ".join(f"{key}: {json.dumps(value)}" for key, value in edge["properties"].items())
            cypher_lines.append(
                "MATCH (a {id: %s}), (b {id: %s}) MERGE (a)-[r:%s]->(b) SET r += {%s};"
                % (json.dumps(edge["source"]), json.dumps(edge["target"]), edge["relation"].upper().replace("-", "_"), props)
            )
        self.cypher_path.write_text("\n".join(cypher_lines), encoding="utf-8")
        self._sync_to_neo4j(graph)
        return graph

    def load_graph(self) -> dict[str, Any]:
        if not self.graph_path.exists():
            self.ensure_assets()
        return json.loads(self.graph_path.read_text(encoding="utf-8"))

    def graph_context(self, message: str, customer_id: int | None, products: list[dict[str, Any]]) -> dict[str, Any]:
        summary = self.load_summary()
        graph = self.load_graph()
        lowered = message.lower()
        category = None
        brand = None
        for item in products or self._catalog(products):
            if str(item.get("category", "")).lower() in lowered and category is None:
                category = str(item.get("category", ""))
            if str(item.get("brand", "")).lower() in lowered and brand is None:
                brand = str(item.get("brand", ""))
        edge_hits = []
        for edge in graph.get("edges", []):
            target = edge.get("target", "")
            if category and target == f"category:{category}":
                edge_hits.append(edge)
            elif brand and target == f"brand:{brand}":
                edge_hits.append(edge)
            elif customer_id and edge.get("source") == f"user:{customer_id}":
                edge_hits.append(edge)
        edge_hits.sort(key=lambda item: item.get("properties", {}).get("weight", 0), reverse=True)
        facts = []
        for edge in edge_hits[:6]:
            facts.append(
                f"{edge['source']} --{edge['relation']}--> {edge['target']} (weight={edge['properties'].get('weight', 1)})"
            )
        return {
            "facts": facts,
            "graph_stats": graph.get("stats", {}),
            "best_model": summary.get("model_report", {}).get("best_model"),
        }

    def load_best_model(self) -> BaseSequenceModel:
        if not self.bundle_path.exists():
            self.ensure_assets()
        payload = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        name = payload.get("best_model", "LSTM")
        model_cls = MODEL_TYPES.get(name, LSTMSequenceModel)
        return model_cls().load(payload.get("models", {}).get(name, {}))

    def _sync_to_neo4j(self, graph: dict[str, Any]) -> None:
        if not self.neo4j_uri:
            return
        try:
            from neo4j import GraphDatabase
        except ModuleNotFoundError:
            return
        try:
            driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
            with driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                for node in graph["nodes"]:
                    session.run(
                        f"MERGE (n:{node['label']} {{id: $id}}) SET n += $props",
                        id=node["id"],
                        props=node["properties"],
                    )
                for edge in graph["edges"]:
                    session.run(
                        "MATCH (a {id: $source}), (b {id: $target}) "
                        f"MERGE (a)-[r:{edge['relation'].upper().replace('-', '_')}]->(b) "
                        "SET r += $props",
                        source=edge["source"],
                        target=edge["target"],
                        props=edge["properties"],
                    )
            driver.close()
        except Exception:
            return

    def score_products_for_user(
        self,
        history_actions: list[str],
        history_categories: list[str],
        products: list[dict[str, Any]],
    ) -> dict[int, float]:
        model = self.load_best_model()
        scores: dict[int, float] = {}
        for product in products:
            pid = int(product["id"])
            scores[pid] = model.score_add_to_cart(
                history_actions=history_actions,
                history_categories=history_categories,
                category=str(product.get("category", "unknown")),
                brand=str(product.get("brand", "Unknown")),
            )
        return scores

    def _build_summary(self, rows: list[dict[str, Any]], catalog: list[dict[str, Any]]) -> dict[str, Any]:
        model_report = self.load_model_report() if self.model_report_path.exists() else {}
        graph = self.load_graph() if self.graph_path.exists() else {}
        action_counts = Counter(row["action"] for row in rows)
        return {
            "dataset": {
                "path": _relative(self.dataset_path),
                "rows": len(rows),
                "sample_20_rows": rows[:20],
                "action_distribution": dict(action_counts),
            },
            "catalog": {
                "products": len(catalog),
                "categories": sorted({item["category"] for item in catalog}),
                "brands": sorted({item["brand"] for item in catalog}),
            },
            "model_report": model_report,
            "graph_report": {
                "path": _relative(self.graph_path),
                "cypher_path": _relative(self.cypher_path),
                "stats": graph.get("stats", {}),
            },
        }
