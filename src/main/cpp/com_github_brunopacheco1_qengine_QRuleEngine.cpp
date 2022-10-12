#include <jni.h>

JNIEXPORT jdouble JNICALL Java_com_github_brunopacheco1_qengine_QRuleEngine_runCircuit
  (JNIEnv *jenv, jclass jcls, jlong jarg1) {
    return jarg1 + 2;
}