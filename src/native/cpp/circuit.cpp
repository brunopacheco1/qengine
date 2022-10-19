#include <qureg.hpp>

void apply_mct(
    iqs::QubitRegister<ComplexDP> psi,
    unsigned const *q_controls,
    unsigned const q_target,
    unsigned const *q_ancillas)
{
    int size_controls = *(&q_controls + 1) - q_controls;
    if (size_controls == 2)
    {
        psi.ApplyToffoli(q_controls[0], q_controls[1], q_target);
        return;
    }

    psi.ApplyToffoli(q_controls[0], q_controls[1], q_ancillas[0]);
    int i = 0;

    for (int j = 2; j < size_controls - 1; j++)
    {
        psi.ApplyToffoli(q_controls[j], q_ancillas[i], q_ancillas[i + 1]);
        i++;
    }
    psi.ApplyToffoli(q_controls[size_controls - 1], q_ancillas[i], q_target);
    for (int j = size_controls - 2; j >= 2; j--)
    {
        psi.ApplyToffoli(q_controls[j], q_ancillas[i - 1], q_ancillas[i]);
        i--;
    }
    psi.ApplyToffoli(q_controls[0], q_controls[1], q_ancillas[i]);
}

void run_circuit()
{
    int num_qubits = 11;
    // Initial state |00000000000>
    std::size_t index = 0;
    iqs::QubitRegister<ComplexDP> psi(num_qubits, "base", index);

    const unsigned ancillas[] = {9, 10};

    apply_mct(psi, unsigned []{ 0, 2 }, 4, ancillas);
    apply_mct(psi, unsigned []{ 1, 2 }, 4, ancillas);
    psi.ApplyPauliX(4);
    apply_mct(psi, unsigned []{ 0, 4 }, 5, ancillas);
    psi.ApplyPauliX(5);
    apply_mct(psi, unsigned []{ 2, 4, 5 }, 6, ancillas);
    psi.ApplyPauliX(6);
    apply_mct(psi, unsigned []{ 3, 4, 5, 6 }, 7, ancillas);
    psi.ApplyPauliX(7);
    apply_mct(psi, unsigned []{ 4, 5, 6, 7 }, 8, ancillas);
    psi.ApplyPauliX(4);
    psi.ApplyPauliX(5);
    psi.ApplyPauliX(6);
    psi.ApplyPauliX(7);

    // Compute the probability of observing qubit 1 in state |1>.

    int measured_qubit = 4;

    double probability = psi.GetProbability(measured_qubit);
    // The expectation value of <Z1> can be computed from the above probability
    double expectation = -1 * probability + 1 * (1 - probability);

    // Draw random number in [0,1)
    double r;
    r = 0.66;
    //  r = np.random.rand() //FIXME
    if (r < probability)
    {
        // Collapse the wavefunction according to qubit 1 being in |1>.
        psi.CollapseQubit(measured_qubit, true);
    }
    else
    {
        // Collapse the wavefunction according to qubit 1 being in |0>
        psi.CollapseQubit(measured_qubit, false);
    }

    // In both cases one needs to re-normalize the wavefunction:
    psi.Normalize();

    psi.Print("Measurement =");

    probability = psi.GetProbability(measured_qubit);

    std::cout << "After collapse, the probability that qubit " << measured_qubit
              << " is in state |1> is " << probability
              << " \t<== should be " << (r < probability ? "1" : "0") << "\n";
}