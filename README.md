# plato-adapters

PLATO adapter implementations — connect PLATO rooms to external services and protocols.

Adapters are the I/O layer for PLATO rooms. A room holds knowledge tiles internally; adapters move data in (via `read()`) and out (via `write()`). They're loaded by [plato-core](https://github.com/SuperInstance/plato-core) via `entry_points` and auto-discovered at startup.

## Adapter Interface

Every adapter implements two methods:

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

## Usage

```python
from plato_core import Room

room = Room("my-room")
room.add_adapter("http-source", url="https://api.example.com/data")
room.add_adapter("webhook-sink", url="https://hooks.example.com/incoming")
```

## Status

Adapter implementations are in development. This repo will contain concrete adapters (HTTP source/sink, file watch, database, etc.) as they're built.

## Related

- [plato-core](https://github.com/SuperInstance/plato-core) — Foundation types + mesh registry
- [plato-mcp](https://github.com/SuperInstance/plato-mcp) — PLATO as MCP tools
- [plato-engine](https://github.com/SuperInstance/plato-engine) — Room lifecycle engine
- [plato-client](https://github.com/SuperInstance/plato-client) — Client library
- [cocapn-plato](https://github.com/SuperInstance/cocapn-plato) — Full PLATO integration
