"""qengine: can a rules engine benefit from quantum computing?"""

from qengine.encoding import VALUES, decode, encode
from qengine.engine import evaluate
from qengine.rules import FIRST_RULE_QUBIT, INPUT_QUBITS, NUM_QUBITS, RULE_COUNT, apply_rules

__all__ = [
    "FIRST_RULE_QUBIT",
    "INPUT_QUBITS",
    "NUM_QUBITS",
    "RULE_COUNT",
    "VALUES",
    "apply_rules",
    "decode",
    "encode",
    "evaluate",
]
