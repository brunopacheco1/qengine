# Implementation plan

The question behind qengine: *can a rules engine do better on a quantum
computer than on a trie?*

Evaluating rules forward has no quantum advantage: the rule circuit only uses
X and multi-controlled X gates on basis states, so it computes exactly what a
few boolean operations would. The plan therefore turns the problem around and
asks **which inputs hit a given rule?**, a search problem that Grover's
algorithm addresses, and then measures what that costs compared to classical
approaches.

The algorithm steps below are written as guidance with checkpoints, not as
solutions.

## Where we are

- [x] Rule set as a CUDA-Q kernel, `apply_rules` (`src/qengine/rules.py`)
- [x] Input encoding and decoding, invalid `11` encodings detected (`encoding.py`)
- [x] Forward evaluation, `evaluate(input1, input2) -> rule` (`engine.py`)
- [x] Tests: full decision table, and `cudaq.adjoint(apply_rules, q)` returns
      the flags to `|0>` for all 16 input states
- [ ] Phase 1: Grover reverse search
- [ ] Phase 2: cost accounting against classical approaches
- [ ] Phase 3: noise and real hardware
- [ ] Phase 4: generated circuits for larger rule sets

## Conventions to keep in mind

| Topic | Convention |
|---|---|
| Qubit layout | q0-1 `input1` (A, B), q2-3 `input2` (A, B), q4-8 rule flags 1-5 |
| `cudaq.sample` bitstrings | **qubit 0 first**: only q2 set prints as `"0010"` |
| `cudaq.get_state` indices | **little-endian**: amplitude index = q0 + 2·q1 + 4·q2 + 8·q3 + ... |
| Kernels | must live in a `.py` file; CUDA-Q reads their source |
| Measuring a sub-register | `mz(q[0:4])` works and returns 4-character bitstrings |

The two bit orders differ. Mixing them up is the most likely source of "Grover
amplified the wrong state" bugs.

## Phase 1: Grover reverse search

**Goal:** `find_inputs(rule) -> list[tuple[Value, Value]]`, returning every
valid input pair that hits `rule`, found with Grover's algorithm and verified
classically. Suggested home: `src/qengine/grover.py`, tests in
`tests/test_grover.py`.

Search space: the 4 input qubits, so N = 16 basis states, of which 9 are
valid encodings.

### 1.1 State preparation

Allocate 9 qubits and put the 4 input qubits in an equal superposition with
Hadamards. The rule flags stay at `|0>`.

**Checkpoint:** `cudaq.get_state` shows 16 amplitudes of 0.25 at indices
0-15 and nothing above index 15.

### 1.2 Oracle: compute, phase flip, uncompute

1. `apply_rules(q)` writes the rule flags.
2. Flip the phase of the states whose flag for the target rule is 1
   (flag qubit = `3 + rule`).
3. `cudaq.adjoint(apply_rules, q)` clears the flags again. Without this the
   flags stay entangled with the inputs and the interference Grover relies on
   breaks.

**Checkpoint:** run the state preparation plus a single oracle (no diffusion)
and inspect `get_state`. The marked states have amplitude -0.25, all others
+0.25, and everything above index 15 is 0.

### 1.3 Exclude invalid encodings

`11` is not a valid value, but the circuit still assigns those states a rule:

| Rule | Valid matches (M) | Invalid states that also hit it |
|---|---|---|
| 1 | 2 | `1011`, `0111` |
| 2 | 2 | `1100`, `1101`, `1110`, `1111` |
| 3 | 1 | `0011` |
| 4 | 2 | none |
| 5 | 2 | none |

Without filtering, rule 2 has 6 matches instead of 2 and Grover would spend
most of its amplitude on inputs that can't occur. The oracle should flip the
phase only when *flag AND input1 valid AND input2 valid*. Two ways to do it:

- **With ancillas:** add two qubits that compute "input1 is valid" and
  "input2 is valid", use them as extra controls on the phase flip, then
  uncompute them. Simple to reason about, costs 2 qubits.
- **Without ancillas:** over GF(2),
  `f·¬a·¬b = f ⊕ f·a ⊕ f·b ⊕ f·a·b`, where `f` is the flag, `a` is
  "q0 and q1" and `b` is "q2 and q3". Each term is one multi-controlled Z,
  and phases multiply, so four phase flips give exactly the condition you
  want.

**Checkpoint:** repeat the 1.2 check for rule 2. Only `1000` and `1001`
(sample order) are negative.

### 1.4 Diffusion

Inversion about the mean on the 4 input qubits: H on all, X on all, a Z on
one input controlled by the other three, X on all, H on all. `z.ctrl` takes
several controls directly, so no Toffoli decomposition is needed.

**Checkpoint:** one full iteration (oracle + diffusion) for rule 3 puts about
0.473 probability on `0010`.

### 1.5 Number of iterations

With N = 16, success probability after k iterations is
`sin²((2k+1)·θ)` with `θ = asin(√(M/N))`:

| M | k=1 | k=2 | k=3 | k=4 |
|---|---|---|---|---|
| 1 (rule 3) | 0.473 | 0.908 | **0.961** | 0.582 |
| 2 (rules 1, 2, 4, 5) | 0.781 | **0.945** | 0.330 | 0.012 |

Too many iterations overshoots. M is part of the answer, so don't hard-code it
per rule. The standard approach when M is unknown is to try increasing k
(here k = 1, 2, 3, since `⌊π/4·√16⌋ = 3`), sample each run, and keep only
verified candidates.

### 1.6 Readout and verification

1. Sample the input register only (`mz(q[0:4])`) with a modest number of
   shots per k.
2. `decode` each bitstring and drop invalid ones (`None`).
3. Check each candidate with `evaluate` and keep it only if it hits the
   target rule. Checking is cheap, which is the premise of Grover.
4. Return the distinct verified pairs.

### 1.7 Tests

Expected results (sample bitstring order, q0 first):

| Rule | Inputs | Bitstrings |
|---|---|---|
| 1 | (A, A), (B, A) | `1010`, `0110` |
| 2 | (A, None), (A, B) | `1000`, `1001` |
| 3 | (None, A) | `0010` |
| 4 | (None, B), (B, B) | `0001`, `0101` |
| 5 | (None, None), (B, None) | `0000`, `0100` |

Suggested tests:

- **Always the same result** (uses `get_state`, no sampling): rule 3 with
  k = 3 has at least 0.96 probability on `0010`. Rule 1 with k = 2 has about
  0.945 split between `1010` and `0110`.
- **Uncompute:** for every rule and k, no probability above state-vector
  index 15.
- **End to end:** `find_inputs(rule)` returns the table above for every rule.
  This one samples, so use enough shots that missing a match is negligible.
- **Validity:** no invalid encoding is ever returned.

## Phase 2: cost accounting

Answer the README question with numbers, not intuition.

- **Queries:** Grover needs about `π/4·√(N/M)` oracle calls. A classical
  brute force needs about `N/M` evaluations on average to find one match, and
  N to find all of them. A trie or a precomputed reverse index answers in
  roughly constant time after building it once.
- **Gates:** count what one oracle call costs once multi-controlled gates are
  decomposed for hardware. `cudaq.estimate_resources` and `cudaq.translate`
  (for example to OpenQASM) are the starting points.
- **Comparison:** at N = 16 the answer will clearly favour classical. The
  useful output is the crossover reasoning: how N, M, oracle depth and
  hardware speed would have to scale for Grover to win.

## Phase 3: noise and real hardware

- Add a CUDA-Q noise model (e.g. depolarizing noise on two-qubit gates) and
  measure how the success probabilities from 1.5 degrade.
- Run the same kernel through `cudaq-ibm-backend`: first its local noisy
  simulation, then a real IBM device (this uses QPU minutes). Multi-controlled
  gates expand into many CNOTs, so expect the oracle depth to dominate.

## Phase 4: larger rule sets

Hand-writing `apply_rules` doesn't scale. Generate the circuit from a
declarative rule definition (inputs, allowed values, ordered conditions)
so that N can grow and the Phase 2 comparison can be repeated at sizes where
it starts to mean something.

## Out of scope

- REST API and the Java stack (removed in the CUDA-Q migration)
- GPU simulation: at 9-11 qubits CPU simulation is instant
