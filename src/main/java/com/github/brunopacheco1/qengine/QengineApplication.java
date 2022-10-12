package com.github.brunopacheco1.qengine;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class QengineApplication {

	static {
		System.loadLibrary("qengine");
	}

	public static void main(String[] args) {
		qengine.run_circuit(1);
		SpringApplication.run(QengineApplication.class, args);
	}

}
