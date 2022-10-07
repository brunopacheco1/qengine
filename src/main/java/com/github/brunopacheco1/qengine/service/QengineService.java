package com.github.brunopacheco1.qengine.service;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;

import javax.annotation.PostConstruct;

import org.redfx.strange.Gate;
import org.redfx.strange.Program;
import org.redfx.strange.Qubit;
import org.redfx.strange.Result;
import org.redfx.strange.Step;
import org.redfx.strange.gate.Cnot;
import org.redfx.strange.gate.Hadamard;
import org.redfx.strange.gate.Measurement;
import org.redfx.strange.gate.X;
import org.redfx.strange.local.SimpleQuantumExecutionEnvironment;
import org.springframework.stereotype.Service;

import com.github.brunopacheco1.qengine.bean.Input;
import com.github.brunopacheco1.qengine.bean.Output;

@Service
public class QengineService {

    private final Map<String, Output> rules = Map.of(
        "00001", Output.builder().ruleId("1").build(),
        "00010", Output.builder().ruleId("2").build(),
        "00100", Output.builder().ruleId("3").build(),
        "01000", Output.builder().ruleId("4").build(),
        "10000", Output.builder().ruleId("5").build()
    );

    private Program program;
    
    @PostConstruct
    private void buildCircuit() {
        program = new Program(6);
        Gate controlX1 = new Cnot(0, 4);
        Step step1 = new Step();
        step1.addGate(controlX1);
        program.addStep(step1);
        Gate controlX2 = new Cnot(2, 5);
        Step step2 = new Step();
        step2.addGate(controlX2);
        program.addStep(step2);
    }
    
    public Output hitRules(Input input) {
        initializeQubits(input);

        SimpleQuantumExecutionEnvironment sqee = new SimpleQuantumExecutionEnvironment();
        Result res = sqee.runProgram(program);
        Qubit[] qubits = res.getQubits();
        List.of(qubits).forEach(q -> System.out.println("qubit with probability on 1 = "+q.getProbability()+", measured it gives "+ q.measure()));

        return Output.builder()
            .build();
    }

    private void initializeQubits(Input input) {
        var input1 = parseInput1(input);
        var input2 = parseInput2(input);
        var index = 0;

        for(Character character : input1.toCharArray()) {
            program.initializeQubit(index++, Double.valueOf(character.toString()));
        }
        
        for(Character character : input2.toCharArray()) {
            program.initializeQubit(index++, Double.valueOf(character.toString()));
        }
    }

    private String parseInput1(Input input) {
        var value = Optional.ofNullable(input).map(Input::getInput1).orElse("");
        switch(value) {
            case "A": return "10";
            case "B": return "01";
            default: return "00";
        }
    }

    private String parseInput2(Input input) {
        var value = Optional.ofNullable(input).map(Input::getInput2).orElse("");
        switch(value) {
            case "A": return "10";
            case "B": return "01";
            default: return "00";
        }
    }
}
