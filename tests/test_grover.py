"""Acceptance tests for Phase 1 (docs/implementation-plan.md, step 1.7).

They are skipped until `src/qengine/grover.py` exists, and each group is
skipped until the function it needs exists. The tests only assume two plain
Python functions, so the kernels behind them can have any shape:

    find_inputs(rule) -> list[tuple[Value, Value]]
        Every valid input pair that hits `rule`.

    grover_state(rule, iterations) -> cudaq.State
        The state after the state preparation and `iterations` rounds of
        oracle + diffusion, with no measurement. Usually one line:
        `return cudaq.get_state(some_kernel, rule, iterations)`.

The state tests compare probabilities, not amplitudes, so a global phase
(for example a diffusion that is the negative of the textbook one) is fine.
"""

import math

import pytest

from qengine import decode, encode, evaluate, input_probabilities, leaked_probability
from qengine.statevector import INPUT_BITSTRINGS

grover = pytest.importorskip("qengine.grover", reason="Phase 1 is not implemented yet")

# Every valid input pair per rule: the decision table, read in reverse.
EXPECTED_INPUTS = {
    1: {("A", "A"), ("B", "A")},
    2: {("A", None), ("A", "B")},
    3: {(None, "A")},
    4: {(None, "B"), ("B", "B")},
    5: {(None, None), ("B", None)},
}
RULES = list(EXPECTED_INPUTS)
SEARCH_SPACE = len(INPUT_BITSTRINGS)  # N = 16
INVALID_BITSTRINGS = [bits for bits in INPUT_BITSTRINGS if decode(bits) is None]
MAX_ITERATIONS = 4  # one more than the useful maximum, to see the overshoot


def matching_bitstrings(rule: int) -> list[str]:
    return ["".join(map(str, encode(*pair))) for pair in sorted(EXPECTED_INPUTS[rule], key=str)]


def success_probability(matches: int, iterations: int) -> float:
    """sin^2((2k+1)·theta) with theta = asin(sqrt(M/N)), from step 1.5."""
    theta = math.asin(math.sqrt(matches / SEARCH_SPACE))
    return math.sin((2 * iterations + 1) * theta) ** 2


@pytest.fixture
def find_inputs():
    if not hasattr(grover, "find_inputs"):
        pytest.skip("qengine.grover.find_inputs does not exist yet")
    return grover.find_inputs


@pytest.fixture
def grover_state():
    if not hasattr(grover, "grover_state"):
        pytest.skip("qengine.grover.grover_state does not exist yet")
    return grover.grover_state


# --- State tests: exact, no sampling ---------------------------------------


@pytest.mark.parametrize("rule", RULES)
def test_zero_iterations_is_the_equal_superposition(grover_state, rule):
    # Step 1.1: every input state has probability 1/16 before any oracle call.
    probabilities = input_probabilities(grover_state(rule, 0))
    assert probabilities == pytest.approx(dict.fromkeys(INPUT_BITSTRINGS, 1 / SEARCH_SPACE))


@pytest.mark.parametrize("iterations", range(MAX_ITERATIONS + 1))
@pytest.mark.parametrize("rule", RULES)
def test_flags_are_uncomputed(grover_state, rule, iterations):
    # Step 1.2: if the flags are not cleared after each oracle call, they stay
    # entangled with the inputs and the diffusion step stops working.
    assert leaked_probability(grover_state(rule, iterations)) == pytest.approx(0.0, abs=1e-6)


@pytest.mark.parametrize("iterations", range(1, MAX_ITERATIONS + 1))
@pytest.mark.parametrize("rule", RULES)
def test_matches_are_amplified_as_predicted(grover_state, rule, iterations):
    # Steps 1.4 and 1.5: the total probability on the valid matches follows
    # the sin^2 formula, and is shared equally between them. This also fails
    # if invalid encodings are marked (step 1.3), because M would be wrong.
    probabilities = input_probabilities(grover_state(rule, iterations))
    matches = matching_bitstrings(rule)
    expected = success_probability(len(matches), iterations)
    assert sum(probabilities[bits] for bits in matches) == pytest.approx(expected, abs=1e-6)
    for bits in matches:
        assert probabilities[bits] == pytest.approx(expected / len(matches), abs=1e-6)


@pytest.mark.parametrize("rule", RULES)
def test_invalid_encodings_are_not_amplified(grover_state, rule):
    # Step 1.3: `11` inputs hit rules 1, 2 and 3 in the circuit, but the oracle
    # must not mark them. After one iteration an unmarked state has less than
    # its starting probability of 1/16; a marked one has much more.
    probabilities = input_probabilities(grover_state(rule, 1))
    for bits in INVALID_BITSTRINGS:
        assert probabilities[bits] < 1 / SEARCH_SPACE, f"invalid input {bits} was amplified"


def test_plan_reference_numbers(grover_state):
    # The two figures quoted in step 1.7 of the plan.
    rule_3 = input_probabilities(grover_state(3, 3))
    assert rule_3["0010"] >= 0.96
    rule_1 = input_probabilities(grover_state(1, 2))
    assert rule_1["1010"] + rule_1["0110"] == pytest.approx(0.945, abs=1e-3)


# --- End to end: samples, so results are only overwhelmingly likely --------


@pytest.mark.parametrize("rule", RULES)
def test_find_inputs_returns_every_match(find_inputs, rule):
    found = find_inputs(rule)
    assert len(found) == len(set(found)), "matches should be distinct"
    assert set(found) == EXPECTED_INPUTS[rule]


@pytest.mark.parametrize("rule", RULES)
def test_find_inputs_returns_only_verified_valid_pairs(find_inputs, rule):
    # `evaluate` raises ValueError for anything that is not a valid input
    # pair, so this also checks that no `11` encoding slips through.
    for input1, input2 in find_inputs(rule):
        assert evaluate(input1, input2) == rule
