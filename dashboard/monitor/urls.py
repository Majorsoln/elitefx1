"""GLASS BOX urls — panels 9 + attestation + auth. GET-only (read-only monitoring)."""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lessee_home, name="home"),                       # role-aware landing
    path("deck/", views.command_deck, name="deck"),
    path("scorecards/", views.scorecards_list, name="scorecards"),  # DASHBOARD-V2 Awamu 1
    path("scorecards/<str:call_sign>/", views.scorecard_detail, name="scorecard_detail"),
    path("my/", views.lessee_list, name="my_models"),                       # DASHBOARD-V2 Awamu 3
    path("my/<str:call_sign>/", views.lessee_detail, name="my_scorecard"),  # lessee (anonymized)
    path("portfolio/", views.portfolio, name="portfolio"),
    path("actions/", views.live_actions, name="actions"),
    path("compliance/", views.compliance, name="compliance"),
    path("registry/", views.registry, name="registry"),
    path("registry/<str:model_id>/", views.registry_detail, name="registry_detail"),
    path("registry/<str:model_id>/attest.json", views.attestation_json, name="attest_json"),
    path("registry/<str:model_id>/attest.html", views.attestation_html, name="attest_html"),
    path("registry/<str:model_id>/attest.pdf", views.attestation_pdf, name="attest_pdf"),
    path("matrix/", views.matrix, name="matrix"),
    path("matrix/<str:pair>/<str:strategy>/", views.matrix_cell, name="matrix_cell"),
    path("alerts/", views.alerts, name="alerts"),
    path("vps/", views.vps, name="vps"),
    path("ledger/", views.ledger, name="ledger"),
    path("reports/<path:path>", views.report_view, name="report_view"),
    path("audit/", views.audit_trail, name="audit"),
    path("login/", auth_views.LoginView.as_view(template_name="monitor/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
