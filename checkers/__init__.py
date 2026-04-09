"""
Plugin registry for MySQL cluster inspection checkers.

Each checker registers itself via the @register_checker decorator.
The registry maintains insertion order so checks run in a predictable sequence.
"""

_checker_registry = {}


def register_checker(name, description=""):
    """Decorator to register an inspection checker.

    Args:
        name: Unique identifier for this checker.
        description: Human-readable description of what this checker does.
    """
    def decorator(func):
        _checker_registry[name] = {
            "func": func,
            "description": description,
        }
        return func
    return decorator


def get_all_checkers():
    """Return a copy of the checker registry."""
    return dict(_checker_registry)


# Import all checker modules so they self-register on import.
from checkers import connection_count  # noqa: E402, F401
from checkers import topology_scale    # noqa: E402, F401
from checkers import schema_scale      # noqa: E402, F401
