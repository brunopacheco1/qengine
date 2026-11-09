import cudaq
import pytest

from qengine import NUM_QUBITS, apply_rules, decode, encode, evaluate

# The full decision table: every valid input pair and the rule it hits.
DECISION_TABLE = [
    ("A", "A", 1),
    ("B", "A", 1),
    ("A", "B", 2),
    ("A", None, 2),
    (None, "A", 3),
    ("B", "B", 4),
    (None, "B", 4),
    ("B", None, 5),
    (None, None, 5),
]


@pytest.mark.parametrize(("input1", "input2", "rule"), DECISION_TABLE)
def test_evaluate_hits_expected_rule(input1, input2, rule):
    assert evaluate(input1, input2) == rule


@pytest.mark.parametrize(("input1", "input2", "_rule"), DECISION_TABLE)
def test_encode_decode_round_trip(input1, input2, _rule):
    assert decode(encode(input1, input2)) == (input1, input2)


def test_encode_rejects_unknown_value():
    with pytest.raises(ValueError):
        encode("C", None)


@pytest.mark.parametrize("bits", ["1100", "0011", "1111"])
def test_decode_rejects_invalid_encoding(bits):
    assert decode(bits) is None


@cudaq.kernel
def compute_uncompute(bits: list[int]):
    q = cudaq.qvector(9)
    for i in range(4):
        if bits[i] == 1:
            x(q[i])
    apply_rules(q)
    cudaq.adjoint(apply_rules, q)
    mz(q)


@pytest.mark.parametrize("index", range(16))
def test_adjoint_returns_flags_to_zero(index):
    bits = [(index >> i) & 1 for i in range(4)]
    outcome = cudaq.sample(compute_uncompute, bits, shots_count=1).most_probable()
    assert outcome == "".join(map(str, bits)) + "0" * (NUM_QUBITS - 4)
