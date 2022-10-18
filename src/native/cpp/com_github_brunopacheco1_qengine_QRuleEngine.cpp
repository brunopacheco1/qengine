#include "../include/com_github_brunopacheco1_qengine_QRuleEngine.h"
#include "circuit.cpp"
#include <qureg.hpp>

JNIEXPORT jstring JNICALL Java_com_github_brunopacheco1_qengine_QRuleEngine_runCircuit(JNIEnv *env, jobject obj, jstring input)
{
  run_circuit();

  return env->NewStringUTF("00001");
}
