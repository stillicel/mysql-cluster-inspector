"""
Mock metadata discovery layer.

Provides get_cluster_metadata(uuid) which returns cluster topology.
Designed as an interface — replace the mock implementation with a real
REST API call in the future.
"""

import logging

logger = logging.getLogger(__name__)

# Mock data keyed by cluster UUID. In production, this would be a REST call.
_MOCK_CLUSTERS = {
    "cluster-uuid-example-001": {
        "version": "8.0.35",
        "master": {
            "host": "master.cluster001.db.local",
            "port": 3306,
            "role": "master",
        },
        "slaves": [
            {"host": "slave1.cluster001.db.local", "port": 3306, "role": "slave"},
            {"host": "slave2.cluster001.db.local", "port": 3306, "role": "slave"},
        ],
    },
    "cluster-uuid-large-002": {
        "version": "5.7.44",
        "master": {
            "host": "master.cluster002.db.local",
            "port": 3306,
            "role": "master",
        },
        "slaves": [
            {"host": f"slave{i}.cluster002.db.local", "port": 3306, "role": "slave"}
            for i in range(1, 8)  # 7 slaves → triggers topology_scale
        ],
    },
}


def get_cluster_metadata(uuid):
    """Return cluster metadata for the given UUID.

    Args:
        uuid: The cluster UUID string.

    Returns:
        dict with keys: 'version', 'master' (host/port/role),
        'slaves' (list of host/port/role dicts).

    Raises:
        ValueError: If the UUID is not found.
    """
    logger.info("Fetching metadata for cluster UUID: %s", uuid)

    if uuid in _MOCK_CLUSTERS:
        meta = _MOCK_CLUSTERS[uuid]
        logger.info(
            "Cluster %s — version=%s, master=%s:%d, slaves=%d",
            uuid, meta["version"],
            meta["master"]["host"], meta["master"]["port"],
            len(meta["slaves"]),
        )
        return meta

    raise ValueError(
        f"Cluster UUID '{uuid}' not found. "
        f"Available mock UUIDs: {list(_MOCK_CLUSTERS.keys())}"
    )
