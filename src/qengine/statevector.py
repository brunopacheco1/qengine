"""Read a simulated state in the same bit order as `cudaq.sample`.

These helpers are for the checkpoints in docs/implementation-plan.md. A Grover
step is correct when the 16 input states have the expected amplitudes *and*
the rule flags are back at |0>, and both are easy to misread by hand because
CUDA-Q 0.16 exposes a state in three different orders:

    state.amplitude("0010...")  qubit 0 first, like sample bitstrings
    numpy.array(state)[i]       little-endian: i = q0 + 2*q1 + 4*q2 + ...
    state[i]                    big-endian: qubit 0 is the highest bit of i

Everything here uses the first one, so the keys match what `cudaq.sample`
prints and what `qengine.decode` accepts.
"""

import cudaq

from qengine.rules import INPUT_QUBITS

INPUT_BITSTRINGS: tuple[str, ...] = tuple(
    format(i, f"0{INPUT_QUBITS}b") for i in range(2**INPUT_QUBITS)
)


def input_amplitudes(state: cudaq.State) -> dict[str, complex]:
    """Return the amplitude of each input state, with every other qubit at 0.

    Keys are 4-character bitstrings, qubit 0 first. The sign matters: after an
    oracle the marked states are negative, which probabilities would hide.
    """
    padding = "0" * (state.num_qubits() - INPUT_QUBITS)
    amplitudes = state.amplitudes([bits + padding for bits in INPUT_BITSTRINGS])
    return dict(zip(INPUT_BITSTRINGS, amplitudes, strict=True))


def input_probabilities(state: cudaq.State) -> dict[str, float]:
    """Return the probability of each input state, with every other qubit at 0."""
    return {bits: abs(amp) ** 2 for bits, amp in input_amplitudes(state).items()}


def leaked_probability(state: cudaq.State) -> float:
    """Return the probability that some qubit after the inputs is not 0.

    This should be 0 (up to rounding) after every complete oracle call. If it
    is not, the rule flags or ancillas were not uncomputed. They are then
    still entangled with the inputs, and the input states can no longer
    interfere with each other, which is what Grover's diffusion step needs.
    """
    return max(0.0, 1.0 - sum(input_probabilities(state).values()))
