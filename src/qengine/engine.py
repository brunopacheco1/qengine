"""Forward evaluation: which rule does an input pair hit?"""

import cudaq

from qengine.encoding import Value, encode
from qengine.rules import FIRST_RULE_QUBIT, apply_rules


@cudaq.kernel
def evaluate_kernel(bits: list[int]):
    q = cudaq.qvector(9)
    for i in range(4):
        if bits[i] == 1:
            x(q[i])
    apply_rules(q)
    mz(q)


def evaluate(input1: Value, input2: Value) -> int:
    """Return the 1-based id of the rule that the input pair hits."""
    # The input is a basis state and the circuit is classical-reversible,
    # so the outcome is deterministic and one shot is enough.
    counts = cudaq.sample(evaluate_kernel, encode(input1, input2), shots_count=1)
    return fired_rule(counts.most_probable())


def fired_rule(bitstring: str) -> int:
    """Return the rule id from a full measurement bitstring.

    CUDA-Q bitstrings list qubit 0 first.
    """
    flags = bitstring[FIRST_RULE_QUBIT:]
    fired = [i + 1 for i, flag in enumerate(flags) if flag == "1"]
    if len(fired) != 1:
        raise RuntimeError(f"Expected exactly one rule flag, got {bitstring!r}")
    return fired[0]
