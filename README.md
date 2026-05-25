# plato-adapters

> Adapter layer for connecting PLATO to the SuperInstance ecosystem

Part of the [SuperInstance](https://github.com/SuperInstance) music constraint theory ecosystem. Provides adapter modules that bridge the PLATO knowledge server with other SuperInstance services — translating between tile formats, routing queries, and integrating knowledge lookups into constraint pipelines.

## Status

This repository is currently in early development. The adapter interfaces are defined but the implementation is forthcoming as the PLATO system matures.

## Intended Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│ PLATO server │◄───►│ plato-adapters│◄───►│ SuperInstance     │
│ (knowledge)  │     │ (translation) │     │ services          │
└─────────────┘     └──────────────┘     │ (constraint-toolkit│
                                         │  flux-genome, etc) │
                                         └──────────────────┘
```

Adapters translate between:
- **Tiles** (PLATO's knowledge units) and **constraint parameters** (constraint-toolkit format)
- **Room queries** and **tradition lookups** (flux-hyperbolic embeddings)
- **Domain tags** and **genome fitness targets** (flux-genome parameters)

## Related Repos

- [**plato-client**](https://github.com/SuperInstance/plato-client) — Python client for the PLATO server
- [**constraint-toolkit**](https://github.com/SuperInstance/constraint-toolkit) — Constraint satisfaction engine
- [**flux-genome**](https://github.com/SuperInstance/flux-genome) — Genetic evolution of musical genomes
- [**flux-hyperbolic**](https://github.com/SuperInstance/flux-hyperbolic) — Hyperbolic tradition embeddings

## License

MIT
