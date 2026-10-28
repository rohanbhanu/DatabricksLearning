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
            <!DOCTYPE html>
            <html>
            <head>
                <title>Royal Insurance</title>
                <style>
                    body {
                        background: #0b132b;
                        color: white;
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding-top: 100px;
                    }

                    h1 {
                        color: #00d4ff;
                        font-size: 42px;
                    }

                    .status {
                        color: #58e6a9;
                        font-size: 22px;
                        margin-top: 20px;
                    }
                </style>
            </head>

            <body>

                <h1>Royal Insurance</h1>

                <h2>Portfolio Intelligence Dashboard</h2>

                <div class="status">
                    Java 21 + Azul Zulu + Spring Boot is running
                </div>

            </body>
            </html>
            """;
    }

    @GetMapping("/health")
    public String health() {
        return "OK";
    }
}
