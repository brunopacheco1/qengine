# qengine
Can I perform better on a quantum computing than on Trie Tree?

cd src/main/cpp
swig -c++ -java -package com.github.brunopacheco1.qengine -outdir ../java/com/github/brunopacheco1/qengine qengine.i
swig -c++ -java -outdir ../java/ qengine.i
g++ -c -fpic qengine.cpp qengine_wrap.cxx -I$JAVA_HOME/include/darwin -I$JAVA_HOME/include -liqs
cd ../../..
g++ -shared src/main/cpp/qengine.o src/main/cpp/qengine_wrap.o -o lib/libqengine.so -liqs