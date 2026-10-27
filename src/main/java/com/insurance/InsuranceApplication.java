package com.insurance;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class InsuranceApplication {

    public static void main(String[] args) {
        SpringApplication.run(InsuranceApplication.class, args);
    }

    @GetMapping("/")
    public String home() {

        return """
            <html>
            <head>
                <title>Insurance Intelligence</title>
            </head>

            <body style="
                background:#07111f;
                color:white;
                font-family:Arial;
                text-align:center;
                padding-top:100px;">

                <h1>Insurance Portfolio Intelligence</h1>

                <h2 style="color:#51d6ca;">
                    Databricks + Java POC
                </h2>

                <p>
                    Insurance Analytics Platform
                </p>

            </body>
            </html>
            """;
    }

    @GetMapping("/runtime")
    public String runtime() {

        return """
            {
                "javaVersion": "%s",
                "javaVendor": "%s",
                "javaHome": "%s"
            }
            """.formatted(
                System.getProperty("java.version"),
                System.getProperty("java.vendor"),
                System.getProperty("java.home")
            );
    }
}