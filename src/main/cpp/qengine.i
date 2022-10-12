/* qengine.i */
%module qengine
%{
/* Put header files here or function declarations like below */
extern double run_circuit(unsigned int qbit);
%}

extern double run_circuit(unsigned int qbit);