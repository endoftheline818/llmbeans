# llmbeans/recommenders/registry.py
"""Registry for hosting tool flag generators."""

_TOOL_GENERATORS = {}


def register_tool(name: str):
    """Decorator to register a hosting tool flag generator."""
    def decorator(fn):
        _TOOL_GENERATORS[name] = fn
        return fn
    return decorator


def get_available_tools() -> list[str]:
    """Return list of registered hosting tool names."""
    return list(_TOOL_GENERATORS.keys())


def get_tool_generator(name: str):
    """Get the generator function for a given tool name."""
    return _TOOL_GENERATORS.get(name)