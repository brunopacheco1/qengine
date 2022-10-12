package com.github.brunopacheco1.qengine;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class QengineApplication {

	static {
		System.loadLibrary("qengine");
	}

	public static void main(String[] args) {
		SpringApplication.run(QengineApplication.class, args);
	}
}
