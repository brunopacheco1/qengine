# AGENTS.md

Instructions for AI coding agents working in this repository. Humans: see
[README.md](README.md) and [docs/implementation-plan.md](docs/implementation-plan.md).

## What this is

An open-source experiment, and a **learning project** for its owner, Bruno: can a rules
engine do better on a quantum computer than on a trie? A small first-match rule set is
encoded as a reversible [CUDA-Q](https://github.com/NVIDIA/cuda-quantum) circuit. Forward
evaluation has no quantum advantage, so the project explores the reverse question (which
inputs hit a rule?) with Grover's algorithm and compares the cost with classical approaches.

- `src/qengine/encoding.py`: input values to qubits and back; detects invalid `11` encodings.
- `src/qengine/rules.py`: the rule circuit, the `apply_rules` kernel.
- `src/qengine/engine.py`: forward evaluation, `evaluate(input1, input2) -> rule`.
- `src/qengine/statevector.py`: read a `cudaq.State` in `sample` bit order, for the plan's
  checkpoints.
- `tests/`: the full decision table, the uncompute check, and `test_grover.py`, the Phase 1
  acceptance tests, skipped until `src/qengine/grover.py` provides `grover_state` and
  `find_inputs`.

Status and next steps: [docs/implementation-plan.md](docs/implementation-plan.md).

## Division of work

- **Agents may write plumbing**: packaging, test infrastructure, encoding and decoding,
  classical verification and benchmarking harnesses, CI and docs.
- **Bruno owns the quantum side and design decisions**: the Grover oracle and diffusion,
  phase-flip and validity tricks, iteration strategy, changes to the rule circuit
  (`apply_rules`), noise experiments and real hardware runs. Do not implement these unless
  he asks in the task. Explain, give hints, point to the checkpoints in the plan and review
  instead.
- Any choice that is hard to reverse needs his decision.

## Commands

```bash
python3.14 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]" && pytest -q
```

Works on Linux (x86_64, ARM64) and macOS on Apple silicon (CPU simulation). CUDA-Q 0.16 has
wheels for Python 3.11 to 3.14 only, so a newer default `python3` will not install it.

CI (`.github/workflows/tests.yml`) runs the same `pytest` on Linux with Python 3.11 and 3.14
for every pull request and every push to `main`.

## Rules

- **Facts.** Check CUDA-Q behaviour by running it in the `.venv`, not from memory. The
  project pins `cudaq>=0.16,<0.17`.
- **Tests.** Any change to the rule circuit keeps the decision-table and adjoint tests
  passing. If the decision table changes, update the tables in the README and the plan in
  the same change.
- **Docs.** Keep the checklist in `docs/implementation-plan.md` current in the same change as
  the code it describes.
- **Licensing.** Apache-2.0. Keep `LICENSE` and `NOTICE`. Code adapted from elsewhere keeps
  its original header and says it was modified.
- **Writing.** Simple, direct English. Explain the quantum idea behind a step when it is not
  obvious; this is a learning project.
- **Git.** Work on a branch and open a PR; never push to `main` and never rewrite its
  history.
- **Authorship.** Bruno is the author of every commit. An agent commits with `--author` set
  to the identity on the commits of `main` (`git log -1 --format='%an <%ae>' main`) and
  names itself only in a `Co-Authored-By:` trailer. An agent cannot sign with Bruno's key,
  so its commits do not go to `main` as they are: Bruno merges each PR with **Squash and
  merge**, which makes one commit signed by GitHub.

## Gotchas

- **Three bit orders.** `cudaq.sample` bitstrings and `state.amplitude("0010...")` put
  qubit 0 first (only q2 set prints as `"0010"`). `numpy.array(state)` is little-endian
  (index = q0 + 2·q1 + 4·q2 + ...). `state[i]` is big-endian, the opposite. Use the helpers
  in `statevector.py`, which stay in the `sample` order.
- **`get_state` runs measurements.** On a kernel with `mz` it returns one collapsed basis
  state, a different one per call. Inspect a kernel without the measurement.
- **Kernels need a source file.** `@cudaq.kernel` reads the function's source, so kernels
  piped through stdin or defined in a plain REPL fail. Put them in a `.py` file.
- **Invalid encodings still hit rules.** `11` inputs hit rules 1, 2 and 3 (4 of them hit
  rule 2). Anything that searches all 16 input states must exclude them.
- **Sample warning.** CUDA-Q 0.16 warns that `sample` and `observe` will change; pytest
  filters that warning in `pyproject.toml`.
- **Bruno's `cudaq-ibm` container** is a CUDA-Q source build for his `cudaq-ibm-backend`
  project, and this repository is not mounted in it. Use the `.venv` for qengine.
