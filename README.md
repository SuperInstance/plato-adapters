# plato-adapters

PLATO adapter implementations — connect PLATO rooms to external services and protocols.

## What Are Adapters?

PLATO rooms hold knowledge tiles internally. Adapters connect rooms to the outside world — reading from data sources, writing to services, or bridging between protocols.

## Available Adapters

Adapters are loaded by [plato-core](https://github.com/SuperInstance/plato-core) via entry_points and auto-discovered at startup.

## Usage

```python
from plato_core import Room

room = Room("my-room")
room.add_adapter("http-source", url="https://api.example.com/data")
room.add_adapter("webhook-sink", url="https://hooks.example.com/incoming")
```

## Creating Custom Adapters

```python
from plato_core.adapters import BaseAdapter

class MyAdapter(BaseAdapter):
    def read(self):
        """Pull data into the room as tiles."""
        ...

    def write(self, tiles):
        """Push tiles to an external system."""
        ...
```

## Related

- [plato-core](https://github.com/SuperInstance/plato-core) — Foundation types + mesh registry
- [plato-mcp](https://github.com/SuperInstance/plato-mcp) — PLATO as MCP tools
- [plato-engine](https://github.com/SuperInstance/plato-engine) — Room lifecycle engine
- [plato-client](https://github.com/SuperInstance/plato-client) — Client library
- [cocapn-plato](https://github.com/SuperInstance/cocapn-plato) — Full PLATO integration
