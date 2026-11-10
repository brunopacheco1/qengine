import cudaq
import pytest

from qengine import apply_rules, decode, input_amplitudes, input_probabilities, leaked_probability
from qengine.statevector import INPUT_BITSTRINGS


@cudaq.kernel
def only_q2():
    q = cudaq.qvector(9)
    x(q[2])


@cudaq.kernel
def minus_on_q0():
    q = cudaq.qvector(9)
    x(q[0])
    z(q[0])


@cudaq.kernel
def all_inputs(uncompute: bool):
    q = cudaq.qvector(9)
    h(q[0:4])
    apply_rules(q)
    if uncompute:
        cudaq.adjoint(apply_rules, q)


@cudaq.kernel
def all_inputs_with_two_spare_qubits():
    q = cudaq.qvector(11)
    h(q[0:4])


def test_keys_match_sample_bitstrings_and_decode():
    probabilities = input_probabilities(cudaq.get_state(only_q2))
    sampled = cudaq.sample(only_q2, shots_count=1).most_probable()
    assert sampled[:4] == "0010"
    assert probabilities["0010"] == pytest.approx(1.0)
    assert all(decode(bits) is None or len(decode(bits)) == 2 for bits in probabilities)


def test_amplitudes_keep_the_sign():
    assert input_amplitudes(cudaq.get_state(minus_on_q0))["1000"] == pytest.approx(-1.0)


@pytest.mark.parametrize("kernel_and_args", [(all_inputs, True), (all_inputs_with_two_spare_qubits,)])
def test_equal_superposition(kernel_and_args):
    state = cudaq.get_state(*kernel_and_args)
    amplitudes = input_amplitudes(state)
    assert list(amplitudes) == list(INPUT_BITSTRINGS)
    assert all(amp == pytest.approx(0.25) for amp in amplitudes.values())
    assert leaked_probability(state) == pytest.approx(0.0, abs=1e-9)


def test_flags_left_computed_count_as_leak():
    # Every input sets exactly one rule flag, so without the uncompute all of
    # the probability sits in states where some flag is 1.
    assert leaked_probability(cudaq.get_state(all_inputs, False)) == pytest.approx(1.0)
