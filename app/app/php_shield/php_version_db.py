"""
PHP Shield -- PHP version lifecycle data and risk reporting.

Dates are the official php.net supported-versions milestones (active support
end = bug fixes stop; security end = security fixes stop). Branches 5.6
through 7.x ended long ago; 8.x dates are the published schedule.
HEADLINE_CVES are illustrative examples per branch, NOT an exhaustive list.
"""
from datetime import date
from typing import Optional

PHP_EOL_DATA: dict[str, dict[str, date]] = {
    "5.6": {"active_end": date(2017, 1, 19),  "security_end": date(2018, 12, 31)},
    "7.0": {"active_end": date(2018, 1, 4),   "security_end": date(2018, 12, 3)},
    "7.1": {"active_end": date(2019, 12, 1),  "security_end": date(2019, 12, 1)},
    "7.2": {"active_end": date(2020, 11, 30), "security_end": date(2020, 11, 30)},
    "7.3": {"active_end": date(2021, 12, 6),  "security_end": date(2021, 12, 6)},
    "7.4": {"active_end": date(2022, 11, 28), "security_end": date(2022, 11, 28)},
    "8.0": {"active_end": date(2022, 11, 26), "security_end": date(2023, 11, 26)},
    "8.1": {"active_end": date(2023, 11, 25), "security_end": date(2025, 12, 31)},
    "8.2": {"active_end": date(2024, 12, 31), "security_end": date(2026, 12, 31)},
    "8.3": {"active_end": date(2025, 12, 31), "security_end": date(2027, 12, 31)},
    "8.4": {"active_end": date(2026, 12, 31), "security_end": date(2028, 12, 31)},
}

# Illustrative, not exhaustive.
HEADLINE_CVES: dict[str, list[str]] = {
    "5.6": ["CVE-2019-11043 (php-fpm remote code execution)", "CVE-2016-5385 (httpoxy)"],
    "7.0": ["CVE-2019-11043 (php-fpm remote code execution)", "CVE-2018-14883 (heap overflow in exif)"],
    "7.1": ["CVE-2019-11043 (php-fpm remote code execution)", "CVE-2019-9641 (uninitialized read in exif)"],
    "7.2": ["CVE-2019-11043 (php-fpm remote code execution)", "CVE-2021-21703 (php-fpm privilege escalation)"],
    "7.3": ["CVE-2021-21703 (php-fpm privilege escalation)", "CVE-2021-21708 (use-after-free in filter)"],
    "7.4": ["CVE-2022-31625 (uninitialized array in pg_query_params)", "CVE-2022-31626 (buffer overflow in mysqlnd)"],
    "8.0": ["CVE-2023-3824 (phar loading buffer overflow)", "CVE-2022-31629 (cookie injection)"],
    "8.1": ["CVE-2024-4577 (CGI argument injection, Windows)", "CVE-2024-2756 (cookie __Host-/__Secure- bypass)"],
    "8.2": ["CVE-2024-4577 (CGI argument injection, Windows)"],
    "8.3": ["CVE-2024-11233 (stream filter memory issue)"],
    "8.4": [],
}


def _parse_branch(version_string: str) -> Optional[str]:
    parts = (version_string or "").strip().split(".")
    if len(parts) < 2 or not (parts[0].isdigit() and parts[1][:1].isdigit()):
        return None
    minor = "".join(c for c in parts[1] if c.isdigit())
    return f"{parts[0]}.{minor}"


def risk_report(version_string: str, today: Optional[date] = None) -> dict:
    """critical if past security_end, high if past active_end, else low."""
    today = today or date.today()
    branch = _parse_branch(version_string)
    if branch is None or branch not in PHP_EOL_DATA:
        return {
            "branch": branch,
            "risk_level": "unknown",
            "headline": f"PHP version {version_string!r} is not in our lifecycle database.",
            "cves": [],
        }

    eol = PHP_EOL_DATA[branch]
    cves = HEADLINE_CVES.get(branch, [])
    if today > eol["security_end"]:
        level = "critical"
        headline = (f"PHP {branch} stopped receiving security fixes on {eol['security_end']:%B %d, %Y}. "
                    "Newly discovered vulnerabilities will never be patched.")
    elif today > eol["active_end"]:
        level = "high"
        headline = (f"PHP {branch} only receives security fixes (bug fixes ended {eol['active_end']:%B %d, %Y}); "
                    f"support ends {eol['security_end']:%B %d, %Y}.")
    else:
        level = "low"
        headline = f"PHP {branch} is actively supported through {eol['active_end']:%B %d, %Y}."
    return {
        "branch": branch,
        "risk_level": level,
        "headline": headline,
        "active_end": eol["active_end"].isoformat(),
        "security_end": eol["security_end"].isoformat(),
        "cves": cves,
    }
