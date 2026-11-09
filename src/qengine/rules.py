"""The rule set as a reversible CUDA-Q circuit.

Qubit layout (9 qubits):

    0-1  input1  (q0 = "A", q1 = "B")
    2-3  input2  (q2 = "A", q3 = "B")
    4-8  one flag per rule (q4 = rule 1 ... q8 = rule 5)

Rules are first-match: a rule fires only if no earlier rule did.

    1. input2 == "A" and input1 in {"A", "B"}
    2. input1 == "A"
    3. input2 == "A"
    4. input2 == "B"
    5. otherwise (default)

The circuit uses only X and multi-controlled X gates and needs no ancillas.
`cudaq.adjoint(apply_rules, q)` undoes it, returning the flag qubits to |0>.
"""

import cudaq

INPUT_QUBITS = 4
RULE_COUNT = 5
NUM_QUBITS = INPUT_QUBITS + RULE_COUNT
FIRST_RULE_QUBIT = INPUT_QUBITS


@cudaq.kernel
def apply_rules(q: cudaq.qview):
    # While computing, flags 1-4 hold "rule did NOT fire", so later rules can
    # use them directly as positive controls. They are flipped back at the end.

    # Rule 1: input2 == A and (input1 == A or input1 == B)
    x.ctrl(q[0], q[2], q[4])
    x.ctrl(q[1], q[2], q[4])
    x(q[4])

    # Rule 2: input1 == A and not rule 1
    x.ctrl(q[0], q[4], q[5])
    x(q[5])

    # Rule 3: input2 == A and no earlier rule
    x.ctrl(q[2], q[4], q[5], q[6])
    x(q[6])

    # Rule 4: input2 == B and no earlier rule
    x.ctrl(q[3], q[4], q[5], q[6], q[7])
    x(q[7])

    # Rule 5: no earlier rule fired
    x.ctrl(q[4], q[5], q[6], q[7], q[8])

    # Flags 1-4 back to "rule fired"
    x(q[4])
    x(q[5])
    x(q[6])
    x(q[7])
