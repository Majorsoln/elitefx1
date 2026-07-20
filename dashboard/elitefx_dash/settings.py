"""
ELITEFX GLASS BOX — Django settings (read-only monitoring; Doctrine V2 §4 "kioo, si mkono").

- HAKUNA secret/broker creds hapa: SECRET_KEY + paths kupitia env (V2 §5).
- REPO_ROOT (env ELITEFX_REPO_ROOT) = root ya repo — ingest inasoma artifacts kutoka huko (read-only).
- SQLite (Postgres-ready: badilisha DATABASES kupitia env bila kugusa code).
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent            # dashboard/
REPO_ROOT = Path(os.environ.get("ELITEFX_REPO_ROOT", BASE_DIR.parent))  # root ya repo

# Dev default (monitoring ya ndani); production: weka ELITEFX_SECRET_KEY kwenye env
SECRET_KEY = os.environ.get("ELITEFX_SECRET_KEY", "dev-insecure-glassbox-key-change-me")
DEBUG = os.environ.get("ELITEFX_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ELITEFX_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "monitor",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "elitefx_dash.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

WSGI_APPLICATION = "elitefx_dash.wsgi.application"

DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.environ.get("ELITEFX_DB_PATH", str(BASE_DIR / "glassbox.sqlite3")),
}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.environ.get("ELITEFX_STATIC_ROOT", str(BASE_DIR / "staticfiles"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# Artifact paths (read-only; ingest pekee ndiye anayezisoma)
ELITEFX_PATHS = {
    "paper_log": REPO_ROOT / "data" / "paper" / "paper_log.jsonl",
    "model_registry": REPO_ROOT / "docs" / "MODEL_REGISTRY.md",
    "experiment_ledger": REPO_ROOT / "docs" / "EXPERIMENT_LEDGER.md",
    "reports_dir": REPO_ROOT / "reports",
    "lessons_dir": REPO_ROOT / "docs" / "lessons",
    "rmap_parquet": REPO_ROOT / "data" / "strategies" / "rmap_train.parquet",
    "alerts_jsonl": Path(os.environ.get("ELITEFX_ALERTS_PATH",
                                        str(REPO_ROOT / "data" / "monitor" / "alerts.jsonl"))),
    "heartbeat": Path(os.environ.get("ELITEFX_HEARTBEAT_PATH",
                                     str(REPO_ROOT / "data" / "vps" / "heartbeat.json"))),
    "pair_strategy_jsonl": REPO_ROOT / "data" / "strategies" / "pair_strategy.jsonl",
}
