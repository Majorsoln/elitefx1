"""
`python manage.py ingest [--demo]` — READ-ONLY ingest ya artifacts → DB mirror.

--demo: inasoma fixtures za `monitor/fixtures/` (format ILEILE ya artifacts halisi — loaders
zilezile zinajaribiwa) na kuweka is_demo=True (inaonekana WAZI kwenye UI). Bila --demo:
inasoma paths za settings.ELITEFX_PATHS (REPO_ROOT). Artifact haipo → "no data" (KAMWE kubuni).
Idempotent: re-ingest haina duplicate (natural keys).
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from monitor import loaders

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


class Command(BaseCommand):
    help = "Ingest artifacts (read-only) -> DB mirror. --demo hutumia fixtures."

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="tumia demo fixtures (is_demo=True)")

    def handle(self, *args, **opts):
        demo = opts["demo"]
        if demo:
            paths = dict(
                paper_log=FIXTURES / "paper_log.jsonl",
                model_registry=FIXTURES / "MODEL_REGISTRY.md",
                experiment_ledger=FIXTURES / "EXPERIMENT_LEDGER.md",
                reports_dir=FIXTURES / "reports", lessons_dir=FIXTURES / "lessons",
                rmap_parquet=FIXTURES / "rmap_train.parquet",
                pair_strategy_jsonl=FIXTURES / "pair_strategy.jsonl",
                alerts_jsonl=FIXTURES / "alerts.jsonl", heartbeat=FIXTURES / "heartbeat.json")
            repo_root = FIXTURES
        else:
            paths = settings.ELITEFX_PATHS
            repo_root = settings.REPO_ROOT

        steps = [
            ("paper_log", lambda: loaders.load_paper_log(paths["paper_log"], demo)),
            ("model_registry", lambda: loaders.load_model_registry(paths["model_registry"], demo)),
            ("ledger", lambda: loaders.load_ledger(paths["experiment_ledger"], demo)),
            ("reports", lambda: loaders.load_reports(paths["reports_dir"], repo_root, demo)),
            ("lessons", lambda: loaders.load_lessons(paths["lessons_dir"], demo)),
            ("pair_strategy", lambda: loaders.load_pair_strategy(paths["rmap_parquet"],
                                                                 paths["pair_strategy_jsonl"], demo)),
            ("alerts", lambda: loaders.load_alerts(paths["alerts_jsonl"], demo)),
            ("heartbeat", lambda: loaders.load_heartbeat(paths["heartbeat"], demo)),
            ("strategy_perf", lambda: loaders.rebuild_strategy_perf(demo)),
        ]
        for name, fn in steps:
            n, note = fn()
            msg = f"  {name}: {n} records" + (f"  [{note}]" if note else "")
            self.stdout.write(msg)
        self.stdout.write(self.style.SUCCESS(f"ingest done (demo={demo}; read-only)"))
