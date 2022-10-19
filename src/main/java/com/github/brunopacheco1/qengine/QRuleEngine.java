package com.github.brunopacheco1.qengine;

import java.util.Collections;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.redfx.strange.Program;
import org.redfx.strange.Step;
import org.redfx.strange.gate.Toffoli;
import org.redfx.strange.gate.X;
import org.redfx.strange.local.SimpleQuantumExecutionEnvironment;

public class QRuleEngine {

  public native String runCircuit(String input);

  public String runJavaCircuit(String input) {
    var sqee = new SimpleQuantumExecutionEnvironment();

    var circuit = initilize(input);

    var res = sqee.runProgram(circuit);
    var qubits = res.getQubits();
    var result = new StringBuilder()
        .append(qubits[8].measure())
        .append(qubits[7].measure())
        .append(qubits[6].measure())
        .append(qubits[5].measure())
        .append(qubits[4].measure()).toString();
    return result;
  }

  private Program initilize(String input) {
    var circuit = new Program(11);

    var chars = input.toCharArray();
    for (int i = chars.length - 1, j = 0; i >= 0; i--, j++) {
      circuit.initializeQubit(j, Double.parseDouble(String.valueOf(chars[i])));
    }

    rule1(circuit);
    rule2(circuit);
    rule3(circuit);
    rule4(circuit);
    rule5(circuit);

    return circuit;
  }

  private void rule1(Program program) {
    applyMct(program, new int[] { 0, 2 }, 4, new int[] {});
    applyMct(program, new int[] { 1, 2 }, 4, new int[] {});

    var step = new Step();
    step.addGate(new X(4));
    program.addStep(step);
  }

  private void rule2(Program program) {
    applyMct(program, new int[] { 0, 4 }, 5, new int[] {});

    var step = new Step();
    step.addGate(new X(5));
    program.addStep(step);
  }

  private void rule3(Program program) {
    applyMct(program, new int[] { 2, 4, 5 }, 6, new int[] { 9 });

    var step = new Step();
    step.addGate(new X(6));
    program.addStep(step);
  }

  private void rule4(Program program) {
    applyMct(program, new int[] { 3, 4, 5, 6 }, 7, new int[] { 9, 10 });

    var step = new Step();
    step.addGate(new X(7));
    program.addStep(step);
  }

  private void rule5(Program program) {
    applyMct(program, new int[] { 4, 5, 6, 7 }, 8, new int[] { 9, 10 });

    var step = new Step();

    step.addGate(new X(4));
    step.addGate(new X(5));
    step.addGate(new X(6));
    step.addGate(new X(7));
    program.addStep(step);
  }

  private void applyMct(Program program, int[] controlQubits, int targetQubit, int[] ancillas) {
    int sizeControls = controlQubits.length;

    if (sizeControls == 2) {
      var step = new Step();
      step.addGate(new Toffoli(controlQubits[0], controlQubits[1], targetQubit));
      program.addStep(step);
      return;
    }

    AtomicInteger counter = new AtomicInteger(0);
    var range = IntStream.range(2, sizeControls - 1).boxed().collect(Collectors.toList());

    var step = new Step();
    step.addGate(new Toffoli(controlQubits[0], controlQubits[1], ancillas[0]));
    program.addStep(step);

    if (!range.isEmpty()) {
      var step2 = new Step();
      range.forEach((var j) -> {
        int i = counter.getAndIncrement();
        step2.addGate(new Toffoli(controlQubits[j], ancillas[i], ancillas[i + 1]));
      });
      program.addStep(step);
    }

    step = new Step();
    step.addGate(new Toffoli(controlQubits[sizeControls - 1], ancillas[counter.get()], targetQubit));
    program.addStep(step);

    Collections.reverse(range);

    if (!range.isEmpty()) {
      var step3 = new Step();
      range.forEach((var j) -> {
        int i = counter.getAndDecrement();
        step3.addGate(new Toffoli(controlQubits[j], ancillas[i - 1], ancillas[i]));
      });
      program.addStep(step);
    }

    step = new Step();
    step.addGate(new Toffoli(controlQubits[0], controlQubits[1], ancillas[counter.get()]));
    program.addStep(step);
  }
}
