#include <qureg.hpp>

void apply_mct(
    iqs::QubitRegister<ComplexDP> psi,
    unsigned const *q_controls,
    unsigned const q_target,
    unsigned const *q_ancillas)
{
    psi.ApplyToffoli(q_controls[0], q_controls[1], q_ancillas[0]);
    int i = 0;
    int size_controls = *(&q_controls + 1) - q_controls;
    for (int j = 2; j < size_controls - 2; j++)
    {
        psi.ApplyToffoli(q_controls[j], q_ancillas[i], q_ancillas[i + 1]);
        i += 1;
    }
    psi.ApplyToffoli(q_controls[size_controls - 1], q_ancillas[i], q_target);
    for (int j = size_controls - 2; j >= 2; j--)
    {
        psi.ApplyToffoli(q_controls[j], q_ancillas[i - 1], q_ancillas[i]);
        i -= 1;
    }
    psi.ApplyToffoli(q_controls[0], q_controls[1], q_ancillas[i]);

    return;
}

void run_circuit()
{
    int num_qubits = 7;
    // Initial state |1111000>
    std::size_t index = 1 + 2 + 4 + 8;
    iqs::QubitRegister<ComplexDP> psi(num_qubits, "base", index);

    const unsigned controls[] = {0, 1, 2, 3};
    const unsigned ancillas[] = {5, 6};

    apply_mct(psi, controls, 4, ancillas);

    psi.Print("Measurement =");
}