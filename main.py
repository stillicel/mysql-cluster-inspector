#!/usr/bin/env python3
"""
MySQL Cluster Health Inspector — CLI entry point.

Usage:
    python main.py -c config.yaml [--uuid <cluster_uuid>]
"""

import argparse
import logging
import os
import sys
from datetime import datetime

import yaml

from engine import run_inspection


def _setup_logging(log_path):
    """Configure root logger: file handler (DEBUG) + stderr handler (WARNING)."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # File handler — detailed execution log
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
    ))
    root.addHandler(fh)

    # Stderr handler — only warnings and errors surface to terminal
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.WARNING)
    sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root.addHandler(sh)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="MySQL Cluster Health Inspector",
    )
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--uuid",
        default=None,
        help="Cluster UUID (overrides the value in the YAML config).",
    )
    return parser.parse_args()


def main():
    args = _parse_args()

    # Load config
    with open(args.config, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    cluster_uuid = args.uuid or config.get("cluster_uuid")
    if not cluster_uuid:
        print("ERROR: cluster_uuid must be provided via --uuid or in the config file.",
              file=sys.stderr)
        sys.exit(1)

    # Capture a single timestamp for this run — used in all output filenames
    run_timestamp = datetime.now()
    ts = run_timestamp.strftime("%Y%m%d_%H%M%S")

    # Create output directory for this run
    output_dir = "."
    log_filename = f"{cluster_uuid}_{ts}_execution.log"
    log_path = os.path.join(output_dir, log_filename)

    _setup_logging(log_path)
    logger = logging.getLogger(__name__)
    logger.info("CLI invoked with config=%s, uuid=%s", args.config, cluster_uuid)

    try:
        run_inspection(config, cluster_uuid, run_timestamp, output_dir)
    except Exception as exc:
        logger.exception("Fatal error during inspection: %s", exc)
        print(f"\033[91m\033[1mFATAL: {exc}\033[0m", file=sys.stderr)

    # Always exit 0 — the tool completed its execution
    sys.exit(0)


if __name__ == "__main__":
    main()
