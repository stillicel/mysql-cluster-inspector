"""
Output reporter — generates terminal output, JSON report, and text report.

All file names follow the convention:
    {cluster_uuid}_{YYYYMMDD_HHMMSS}_{type}.{extension}
"""

import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

# ANSI codes for terminal highlights
RED = "\033[91m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _status_color(status):
    return GREEN if status == "Healthy" else RED


def generate_terminal_output(results, cluster_uuid):
    """Print a summary to the terminal with color highlighting."""
    print()
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  MySQL Cluster Inspection Report{RESET}")
    print(f"{BOLD}  Cluster UUID: {cluster_uuid}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    print()

    overall_healthy = True
    for name, result in results.items():
        status = result.get("status", "Unknown")
        if status != "Healthy":
            overall_healthy = False

        color = _status_color(status)
        error = result.get("error")

        print(f"  [{color}{BOLD}{status}{RESET}]  {name}")
        if error:
            print(f"         {RED}{BOLD}ERROR: {error}{RESET}")

    print()
    overall = "Healthy" if overall_healthy else "Unhealthy"
    color = _status_color(overall)
    print(f"  {BOLD}Overall Cluster Status: [{color}{overall}{RESET}{BOLD}]{RESET}")
    print(f"{'=' * 60}")
    print()

    if not overall_healthy:
        print(
            f"  {RED}{BOLD}⚠ One or more checks reported Unhealthy. "
            f"Review the reports for details.{RESET}",
            file=sys.stderr,
        )
        print()


def generate_json_report(results, cluster_uuid, run_timestamp, output_dir="."):
    """Write the structured JSON report.

    Returns:
        Path to the written JSON file.
    """
    ts = run_timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{cluster_uuid}_{ts}_report.json"
    filepath = os.path.join(output_dir, filename)

    overall_healthy = all(
        r.get("status") == "Healthy" for r in results.values()
    )

    report = {
        "cluster_uuid": cluster_uuid,
        "timestamp": run_timestamp.isoformat(),
        "overall_status": "Healthy" if overall_healthy else "Unhealthy",
        "checks": results,
    }

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    logger.info("JSON report written to %s", filepath)
    return filepath


def generate_text_report(results, cluster_uuid, run_timestamp, output_dir="."):
    """Write a human-readable text report.

    Returns:
        Path to the written text file.
    """
    ts = run_timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{cluster_uuid}_{ts}_report.txt"
    filepath = os.path.join(output_dir, filename)

    lines = []
    lines.append("=" * 60)
    lines.append("  MySQL Cluster Inspection Report")
    lines.append(f"  Cluster UUID : {cluster_uuid}")
    lines.append(f"  Timestamp    : {run_timestamp.isoformat()}")
    lines.append("=" * 60)
    lines.append("")

    overall_healthy = True
    for name, result in results.items():
        status = result.get("status", "Unknown")
        if status != "Healthy":
            overall_healthy = False

        lines.append(f"--- {name} [{status}] ---")

        for key, value in result.items():
            if key == "status":
                continue
            lines.append(f"  {key}: {_format_value(value)}")

        lines.append("")

    overall = "Healthy" if overall_healthy else "Unhealthy"
    lines.append(f"Overall Cluster Status: {overall}")
    lines.append("=" * 60)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    logger.info("Text report written to %s", filepath)
    return filepath


def _format_value(value, indent=2):
    """Recursively format nested dicts/lists for the text report."""
    if isinstance(value, dict):
        inner = "\n".join(
            f"{'  ' * (indent + 1)}{k}: {_format_value(v, indent + 1)}"
            for k, v in value.items()
        )
        return "\n" + inner
    if isinstance(value, list):
        parts = []
        for item in value:
            parts.append(f"{'  ' * (indent + 1)}- {_format_value(item, indent + 1)}")
        return "\n" + "\n".join(parts)
    return str(value)
