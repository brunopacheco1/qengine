package com.github.brunopacheco1.qengine.service;

import java.util.Map;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.github.brunopacheco1.qengine.QRuleEngine;
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

    private final QRuleEngine engine = new QRuleEngine();

    public Output hitRules(Input input) {
        var inputStr = parseInput(input);
        var outputKey = engine.runJavaCircuit(inputStr);
        return rules.get(outputKey);
    }

    private String parseInput(Input input) {
        var input1 = parseInput1(input);
        var input2 = parseInput2(input);
        return "0000000" + input2 + input1;
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
