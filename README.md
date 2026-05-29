# plato-adapters

**PLATO adapter layer** — connects external services and protocols to the PLATO tile system. Standardized interfaces for fleet agents to interact with PLATO rooms.

## What This Gives You

- **Service adapters** — wrap external APIs as PLATO tile readers/writers
- **Protocol bridges** — translate between PLATO tiles and other formats
- **Room mapping** — map external data structures to PLATO room semantics
- **Standard interface** — consistent API for all fleet integrations

## Installation

```bash
pip install plato-adapters
```

## How It Fits
- [OpenConstruct Documentation](https://github.com/SuperInstance/openconstruct-docs) — ecosystem-wide docs and guides

The integration layer in the PLATO stack: `plato-room` → `plato-adapters` → external services. Used by all domain agents (`capitaine-agent`, `businesslog-agent`, `activeledger-agent`) to write to and read from PLATO.

## License

MIT
