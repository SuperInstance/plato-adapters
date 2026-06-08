# INTEGRATION.md — plato-adapters

## Role in the SuperInstance Ecosystem

plato-adapters is the **adapter pattern library** for the PLATO ecosystem. It provides typed transformations, adapter registries, and chainable pipelines that normalize data flowing between SuperInstance's diverse language runtimes (Rust, Python, Zig, Go) and conceptual layers (creative, constraint, spectral, hyperbolic).

## SuperInstance Integration Points

### 1. constraint-dsl — Input Normalization
- `AdapterRegistry.chain(["parse_tags", "normalize_dials", "embed_poincare"])` converts raw user input into constraint-dsl compatible variables
- `transform.normalize` scales arbitrary numeric ranges to [0, 1] for dial positions
- `transform.encode` serializes Python objects into Rust-compatible structs via JSON

### 2. flux-hyperbolic-rs — Embedding Preprocessing
- `plato_adapters.transform` provides `hyperbolic_project` adapter that ensures points stay inside the Poincaré ball before passing to `PoincareBall::distance()`
- `AdapterRegistry.get("hyperbolic_project")` is used by `TraditionEmbedding::from_dial()` when called from Python via PyO3

### 3. creative-engine-rust — State Serialization
- `CreativeSystem` state vectors are serialized through `transform.encode` for cross-language transport
- `AdapterRegistry.chain(["lorenz_to_json", "osc_bundle", "send"])` enables Python agents to inject perturbations into Rust creative systems

### 4. si-runtime-python — Capability Adapter Discovery
- `si_runtime.cell.Cell` can register adapters for its local capability surface
- `AdapterRegistry` provides `discover()` to list all registered adapters in a fleet
- `si-cli scan` detects adapter registries and includes adapter count in repo capability metrics

### 5. superinstance-live — OSC I/O Bridging
- `OSCBridge` receives untyped `/constraint/{name}/set/{param} f` messages
- `plato-adapters` provides `osc_to_typed` adapter that dispatches on OSC address patterns and converts args to Python types
- `AdapterRegistry.chain(["osc_parse", "type_check", "pipeline_input"])` runs inside `Session._on_osc_constraint_set()`

### 6. si-cli — Adapter Audit
- `si-cli audit` checks that all adapters in a registry have:
  - Valid input/output type annotations
  - No unhandled exceptions in `adapt()`
  - Cycle-free chain definitions
- Results are logged to Supabase `fleet_events`

### 7. constraint-dynamics-rs — Cross-Language Constraint Variables
- `AdapterRegistry` bridges Python constraint specs (dicts) to Rust `Constraint` objects
- `transform.decode` deserializes JSON constraint definitions into `ConstraintNode` structs
- This enables si-runtime-python agents to define constraints that run in constraint-dynamics-rs solvers

## Dial / Room / Snap Compatibility

| Primitive | Mapping |
|-----------|---------|
| **Dial**  | `transform.normalize` maps any input range to [0, 1]; dial position = normalized value |
| **Room**  | Each `AdapterRegistry` instance is scoped to a Room; adapters registered in one Room are not visible in others unless explicitly shared |
| **Snap**  | `registry.snap()` freezes all adapter outputs to their current values, disabling further transformation (passthrough mode) |
| **Cascade**| Child rooms inherit parent registry entries via `registry.fork()`; new entries are local, parent entries are shared read-only |

## Energy Conservation

Adapter transformations carry a computational cost that contributes to the agent's η budget:
- `transform.normalize`: O(n) → cost = 0.01 per element
- `transform.encode/decode`: O(n) → cost = 0.05 per element
- `registry.chain(k adapters)`: cost = Σ individual costs × 1.2 (overhead factor)
- `si-runtime-python.Budget` subtracts adapter costs from η before calling downstream systems

## Quick Start

```python
from plato_adapters import AdapterRegistry, transform

registry = AdapterRegistry()
registry.register("normalize", transform.normalize)
registry.register("encode", transform.encode)

# Chain adapters
pipeline = registry.chain(["normalize", "encode"])
result = pipeline.adapt({"dial": 3.2, "confidence": 0.8})
```

Custom adapter:
```python
from plato_adapters.adapter import Adapter

class ScaleAdapter(Adapter):
    def __init__(self, factor: float):
        self.factor = factor
    def adapt(self, input):
        return {k: v * self.factor for k, v in input.items()}

registry.register("scale", ScaleAdapter(2.0))
```

## Tests

```bash
pytest tests/
```

Registry lookup, chain execution, transform correctness, and fork/isolation tests must pass.
