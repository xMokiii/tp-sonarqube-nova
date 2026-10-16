"""Validate the actual ZAP reports and generate the workflow summary."""

import json
import sys
from collections import Counter
from pathlib import Path


def main():
    folder = Path("/zap/wrk")
    data = json.loads((folder / "zap-report.json").read_text(encoding="utf-8-sig"))
    sites = data.get("site", [])
    if not sites or any(site.get("@name") != "http://app:5000" for site in sites):
        raise ValueError("Unexpected or missing scan target")
    if "<html" not in (folder / "zap-report.html").read_text(encoding="utf-8").lower():
        raise ValueError("The HTML report is not an HTML document")
    alerts = [alert for site in sites for alert in site.get("alerts", [])]
    counts = Counter(str(alert["riskcode"]) for alert in alerts)
    names = {"0": "Informationnel", "1": "Faible", "2": "Moyen", "3": "Eleve"}
    if set(counts) - set(names):
        raise ValueError("Unexpected ZAP risk code")
    summary = {
        "target": "http://app:5000",
        "zap_version": data.get("@version"),
        "created_utc": data.get("created"),
        "alert_entries": len(alerts),
        "distinct_rule_ids": len({alert["pluginid"] for alert in alerts}),
        "instances": sum(len(alert.get("instances", [])) for alert in alerts),
        "risk_counts": {names[key]: counts.get(key, 0) for key in names},
    }
    (folder / "zap-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "## TP3 - Rapport ZAP Baseline",
        "",
        "Cible : `http://app:5000` (laboratoire Docker ephemere, scan anonyme).",
        "",
        "| Risque ZAP | Entrees d'alertes |",
        "|---|---:|",
    ]
    lines.extend("| {} | {} |".format(names[key], counts.get(key, 0)) for key in reversed(names))
    lines.extend([
        "",
        "{} entrees, {} regles distinctes, {} occurrences.".format(
            summary["alert_entries"], summary["distinct_rule_ids"], summary["instances"]
        ),
        "",
        "Les alertes doivent etre qualifiees ; elles ne sont pas toutes des vulnerabilites confirmees.",
        "Le baseline ne demontre pas l'absence d'injection SQL.",
        "Telecharger les rapports HTML/JSON et les journaux dans les artefacts du workflow.",
    ])
    (folder / "zap-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("Invalid ZAP report: {}".format(error), file=sys.stderr)
        sys.exit(3)
