package com.github.brunopacheco1.qengine.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.github.brunopacheco1.qengine.bean.Input;
import com.github.brunopacheco1.qengine.bean.Output;
import com.github.brunopacheco1.qengine.service.QengineService;

import lombok.AllArgsConstructor;

@RestController
@AllArgsConstructor
public class QengineController {
    
    private final QengineService service;

    @PostMapping("/engine")
    public Output hitRules(@RequestBody Input input) {
        return service.hitRules(input);
    }
}
