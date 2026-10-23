"""
PHP Shield -- tier catalog and the scan -> tier recommendation.
All numbers/thresholds live in tiers.yaml; this module only applies them.
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from app.php_shield.php_version_db import PHP_EOL_DATA

_DIR = Path(__file__).parent
TIER_ORDER = ("basic", "standard", "complex")


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return yaml.safe_load((_DIR / "tiers.yaml").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def checklist_template() -> list[dict]:
    return yaml.safe_load((_DIR / "delivery_checklist.yaml").read_text(encoding="utf-8"))["items"]


def reload() -> None:
    _cfg.cache_clear()
    checklist_template.cache_clear()


def tier_catalog() -> list[dict]:
    t = _cfg()["tiers"]
    return [{"key": k, **t[k]} for k in TIER_ORDER]


def maintenance_plan() -> dict:
    return dict(_cfg()["maintenance"])


def tier_price_cents(key: str) -> int:
    return int(_cfg()["tiers"][key]["price_cents"])


def tier_name(key: Optional[str]) -> str:
    return _cfg()["tiers"][key]["name"] if key else "Maintenance Plan only"


def _branch_key(b: str) -> tuple:
    major, minor = b.split(".")
    return int(major), int(minor)


def branches_behind(branch: Optional[str]) -> Optional[int]:
    if not branch or branch not in PHP_EOL_DATA:
        return None
    mine = _branch_key(branch)
    return sum(1 for b in PHP_EOL_DATA if _branch_key(b) > mine)


def recommend(scan: dict) -> dict:
    """scan = ScanResult.to_dict(). Returns {tier, reason, custom_quote, score}."""
    risk = scan.get("risk") or {}
    behind = branches_behind(risk.get("branch"))
    if not scan.get("php_detected") or not scan.get("version") or behind is None:
        return {
            "tier": None,
            "custom_quote": True,
            "score": None,
            "reason": "We couldn't pin down your exact PHP version from public signals, so we can't price this "
                      "accurately. Request a custom quote and we'll take a closer look.",
        }

    cfg = _cfg()
    sc = cfg["scoring"]
    score, why = 0, []

    pts = sc["risk_level"].get(risk.get("risk_level"), 0)
    if pts:
        score += pts
        why.append("support for this PHP version has ended" if risk["risk_level"] == "critical"
                   else "this PHP version no longer gets routine fixes")

    gap_pts = 0
    for rule in sorted(sc["version_gap"], key=lambda r: -r["min_branches_behind"]):
        if behind >= rule["min_branches_behind"]:
            gap_pts = rule["points"]
            break
    if gap_pts:
        score += gap_pts
        why.append(f"it is {behind} releases behind the latest")

    if len(risk.get("cves") or []) >= sc["cve_count"]["min"]:
        score += sc["cve_count"]["points"]
        why.append("several known vulnerabilities apply")

    if scan.get("wordpress"):
        score += sc["wordpress_points"]
        why.append("WordPress plugins and themes will need compatibility work")

    th = cfg["thresholds"]
    tier = "basic" if score <= th["basic_max_score"] else "standard" if score <= th["standard_max_score"] else "complex"
    reason = f"PHP {risk.get('branch')}: " + ("; ".join(why) if why else "a small, low-risk upgrade") + "."
    return {"tier": tier, "custom_quote": False, "score": score, "reason": reason[0].upper() + reason[1:]}
