# qengine

Can a rules engine do better on a quantum computer than on a trie?

qengine encodes a small first-match rule set as a reversible quantum circuit
with [CUDA-Q](https://github.com/NVIDIA/cuda-quantum). Evaluating rules
forward gives no quantum advantage: the circuit only uses X and
multi-controlled X gates on basis states, so it computes exactly what a few
boolean operations would. The interesting direction is the reverse
question, *which inputs hit a given rule?*, which is a search problem that
Grover's algorithm can address. See the
[implementation plan](docs/implementation-plan.md).

## The rules

Two inputs, each `"A"`, `"B"` or `None`. The first rule that matches wins:

| Rule | Condition |
|---|---|
| 1 | `input2 == "A"` and `input1` is `"A"` or `"B"` |
| 2 | `input1 == "A"` |
| 3 | `input2 == "A"` |
| 4 | `input2 == "B"` |
| 5 | otherwise |

## Qubit layout

| Qubits | Meaning |
|---|---|
| 0-1 | `input1`: q0 = `"A"`, q1 = `"B"` |
| 2-3 | `input2`: q2 = `"A"`, q3 = `"B"` |
| 4-8 | one flag per rule: q4 = rule 1 ... q8 = rule 5 |

`11` is not a valid input encoding, but the circuit still assigns it a rule
(e.g. `input1 = 11` hits rule 2), so searches over all 16 input states need to
exclude it. CUDA-Q bitstrings list **qubit 0 first**.

## Layout

| Path | Contents |
|---|---|
| `src/qengine/encoding.py` | input values to qubits and back |
| `src/qengine/rules.py` | the rule circuit (`apply_rules` kernel) |
| `src/qengine/engine.py` | forward evaluation: input pair to rule id |
| `src/qengine/statevector.py` | read a simulated state in `sample` bit order |
| `tests/` | the full decision table, an uncompute check, and the Phase 1 acceptance tests (skipped until `grover.py` exists) |
| `docs/` | the [implementation plan](docs/implementation-plan.md) |
| `AGENTS.md` | instructions for AI coding agents |

## Setup

CUDA-Q 0.16 has wheels for Python 3.11 to 3.14, on Linux (x86_64, ARM64) and
macOS on Apple silicon (CPU simulation only).

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest
```

```python
from qengine import evaluate

evaluate("A", None)  # 2
```

## License

Apache License 2.0, see [LICENSE](LICENSE) and [NOTICE](NOTICE).
