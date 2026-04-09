"""
Core inspection engine.

Loads checkers from the registry, connects to nodes, runs each checker,
and delegates reporting.
"""

import logging

import pymysql

from checkers import get_all_checkers
from metadata import get_cluster_metadata
from reporter import (
    generate_json_report,
    generate_terminal_output,
    generate_text_report,
)

logger = logging.getLogger(__name__)


def _make_connect_func(username, password, mysql_version):
    """Return a connect_func(host, port) that creates a PyMySQL connection.

    The function also stores the MySQL version string so checkers can branch
    on version-specific SQL if needed.
    """
    def connect(host, port):
        logger.debug("Connecting to %s:%d as %s", host, port, username)
        conn = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            connect_timeout=10,
            read_timeout=30,
        )
        conn._mysql_version = mysql_version
        return conn
    return connect


def run_inspection(config, cluster_uuid, run_timestamp, output_dir="."):
    """Run all registered checkers against the target cluster.

    Args:
        config: dict with 'username' and 'password'.
        cluster_uuid: The target cluster UUID.
        run_timestamp: datetime captured at CLI start, shared across all outputs.
        output_dir: Directory for report files.

    Returns:
        dict of checker results keyed by checker name.
    """
    logger.info("Inspection started at %s for cluster %s", run_timestamp.isoformat(), cluster_uuid)

    # Step 1: Discover cluster metadata
    cluster_meta = get_cluster_metadata(cluster_uuid)
    mysql_version = cluster_meta.get("version", "unknown")
    logger.info("Cluster MySQL version: %s", mysql_version)

    # Step 2: Build the connection factory
    connect_func = _make_connect_func(
        config["username"], config["password"], mysql_version,
    )

    # Step 3: Execute each registered checker
    checkers = get_all_checkers()
    results = {}

    for name, entry in checkers.items():
        desc = entry["description"]
        func = entry["func"]
        logger.info("Running checker: %s — %s", name, desc)

        try:
            result = func(cluster_meta, connect_func)
            results[name] = result
            logger.info("Checker '%s' completed — status=%s", name, result.get("status"))
        except Exception as exc:
            logger.exception("Checker '%s' crashed: %s", name, exc)
            results[name] = {
                "status": "Unhealthy",
                "error": f"Checker crashed: {exc}",
            }

    # Step 4: Generate outputs
    generate_terminal_output(results, cluster_uuid)
    json_path = generate_json_report(results, cluster_uuid, run_timestamp, output_dir)
    text_path = generate_text_report(results, cluster_uuid, run_timestamp, output_dir)

    logger.info("Reports written: %s, %s", json_path, text_path)
    logger.info("Inspection finished.")

    return results
