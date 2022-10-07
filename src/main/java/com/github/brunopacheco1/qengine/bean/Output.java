package com.github.brunopacheco1.qengine.bean;

import lombok.Builder;
import lombok.Data;
import lombok.extern.jackson.Jacksonized;

@Data
@Builder
@Jacksonized
public class Output {
    private final String ruleId;
}
