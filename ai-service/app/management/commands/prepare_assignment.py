from django.core.management.base import BaseCommand

from app.assignment import AssignmentPipelineService


class Command(BaseCommand):
    help = "Sinh dataset, train 3 mo hinh, build KB graph va tao bao cao cho bai AISERVICE."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Tao lai toan bo artefact.")

    def handle(self, *args, **options):
        summary = AssignmentPipelineService().ensure_assets(force=bool(options.get("force")))
        self.stdout.write(self.style.SUCCESS("Da tao xong artefact AISERVICE"))
        self.stdout.write(f"Dataset: {summary['dataset']['path']}")
        self.stdout.write(f"Best model: {summary['model_report'].get('best_model')}")
        self.stdout.write(f"Graph: {summary['graph_report']['path']}")
