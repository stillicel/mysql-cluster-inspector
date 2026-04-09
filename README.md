# MySQL Cluster Health Inspector

A Python-based CLI tool for inspecting the health of Percona MySQL 5.7/8.x clusters. It connects to all nodes in a cluster, runs a suite of pluggable health checks, and produces both terminal output and persistent reports.

## Key Features

- **Connection Count** -- Checks `Threads_connected` on every node (master + slaves) against a configurable threshold (default: 3,500).
- **Topology Scale** -- Validates that the number of slave nodes does not exceed the allowed maximum (default: 5).
- **Schema Scale** -- Inspects the master node for excessive user databases and InnoDB table counts.
- **Color-coded terminal output** with an overall Healthy / Unhealthy verdict.
- **JSON & plain-text reports** saved with a `{ClusterUUID}_{Timestamp}` naming convention for easy traceability.

## Architecture

The project follows a **plugin-based design**:

```
main.py          CLI entry point & logging setup
engine.py        Orchestrator -- discovers metadata, runs checkers, generates reports
metadata.py      Cluster metadata discovery (mock layer; swap for a real API)
reporter.py      Terminal, JSON, and text report generators
checkers/
  __init__.py    Plugin registry (@register_checker decorator)
  connection_count.py
  topology_scale.py
  schema_scale.py
```

Adding a new check is as simple as creating a new file under `checkers/`, decorating your function with `@register_checker`, and importing it in `checkers/__init__.py`.

All output files (reports and execution logs) follow the naming convention:

```
{cluster_uuid}_{YYYYMMDD_HHMMSS}_report.json
{cluster_uuid}_{YYYYMMDD_HHMMSS}_report.txt
{cluster_uuid}_{YYYYMMDD_HHMMSS}_execution.log
```

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `PyMySQL`, `PyYAML`.

## Usage

```bash
# Basic usage with a config file
python main.py -c config.yaml

# Override the cluster UUID from the command line
python main.py -c config.yaml --uuid cluster-uuid-example-001
```

### Configuration

Create a `config.yaml` with your database credentials and target cluster:

```yaml
username: "dba_admin"
password: "your_password_here"
cluster_uuid: "cluster-uuid-example-001"
```

## License

MIT
