#include "../include/com_github_brunopacheco1_qengine_QRuleEngine.h"
#include <qureg.hpp>

JNIEXPORT jstring JNICALL Java_com_github_brunopacheco1_qengine_QRuleEngine_runCircuit(JNIEnv *env, jobject obj, jstring input)
{
  int num_qubits = 2;
  iqs::QubitRegister<ComplexDP> psi(num_qubits, "base", 0);

  psi.Print("Initial state =");

  psi.ApplyHadamard(0);
  psi.ApplyCPauliX(0, 1);

  psi.Print("Measurement =");

  return env->NewStringUTF("00001");
}
