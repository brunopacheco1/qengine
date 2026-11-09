"""Two-qubit encoding of the engine's inputs.

Each input is "A", "B" or None (no value), stored as one-hot bits:
the first qubit means "A", the second means "B". Both set ("11") is not a
valid encoding, but the circuit still produces an answer for it, so anything
that explores the full 4-qubit input space (e.g. a search) must filter it out.
"""

Value = str | None

VALUES: tuple[Value, ...] = (None, "A", "B")

_TO_BITS: dict[Value, tuple[int, int]] = {None: (0, 0), "A": (1, 0), "B": (0, 1)}
_FROM_BITS = {bits: value for value, bits in _TO_BITS.items()}


def encode(input1: Value, input2: Value) -> list[int]:
    """Return the input qubits [q0, q1, q2, q3] for an input pair."""
    for value in (input1, input2):
        if value not in _TO_BITS:
            raise ValueError(f"Unknown input value {value!r}, expected one of {VALUES}")
    return [*_TO_BITS[input1], *_TO_BITS[input2]]


def decode(bits: list[int] | str) -> tuple[Value, Value] | None:
    """Return the input pair for qubits [q0, q1, q2, q3], or None if invalid."""
    q = [int(b) for b in bits]
    if len(q) != 4:
        raise ValueError(f"Expected 4 input bits, got {len(q)}")
    input1 = _FROM_BITS.get((q[0], q[1]), "invalid")
    input2 = _FROM_BITS.get((q[2], q[3]), "invalid")
    if input1 == "invalid" or input2 == "invalid":
        return None
    return input1, input2
