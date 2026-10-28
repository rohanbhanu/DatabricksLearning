package com.insurance;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;

@SpringBootApplication
@RestController
public class InsuranceApplication {

    private final DatabricksService databricksService;

    public InsuranceApplication(
            DatabricksService databricksService
    ) {
        this.databricksService = databricksService;
    }

    public static void main(String[] args) {
        SpringApplication.run(
                InsuranceApplication.class,
                args
        );
    }

    @GetMapping("/")
    public String home() {

        return """
            <!DOCTYPE html>
            <html lang="en">

            <head>
                <meta charset="UTF-8">
                <meta name="viewport"
                      content="width=device-width, initial-scale=1.0">

                <title>Royal Insurance</title>

                <style>

                    * {
                        box-sizing: border-box;
                    }

                    body {
                        margin: 0;
                        min-height: 100vh;
                        background:
                            radial-gradient(
                                circle at top right,
                                #16345f,
                                transparent 38%
                            ),
                            linear-gradient(
                                135deg,
                                #071426,
                                #0b1f3a
                            );
                        color: #ffffff;
                        font-family:
                            Arial,
                            Helvetica,
                            sans-serif;
                    }

                    .container {
                        width: min(1400px, 94%);
                        margin: 0 auto;
                        padding: 40px 0 70px;
                    }

                    .header {
                        margin-bottom: 32px;
                    }

                    .brand {
                        color: #45ddff;
                        font-size: 18px;
                        font-weight: 700;
                        letter-spacing: 3px;
                        text-transform: uppercase;
                    }

                    h1 {
                        margin: 10px 0 8px;
                        font-size: clamp(32px, 5vw, 54px);
                    }

                    .subtitle {
                        color: #a8bad2;
                        font-size: 17px;
                    }

                    .status {
                        display: inline-block;
                        margin-top: 16px;
                        padding: 8px 15px;
                        border: 1px solid #20d89b;
                        border-radius: 999px;
                        color: #62f6c3;
                        background: rgba(32, 216, 155, 0.08);
                    }

                    .section-title {
                        margin: 34px 0 18px;
                        color: #dcecff;
                        font-size: 20px;
                    }

                    .message {
                        padding: 18px;
                        border-radius: 14px;
                        background: rgba(255, 255, 255, 0.06);
                        color: #bcd0e9;
                    }

                    .message.error {
                        border: 1px solid #ff6f7d;
                        color: #ffb2bb;
                    }

                    .kpi-grid {
                        display: grid;
                        grid-template-columns:
                            repeat(auto-fit, minmax(220px, 1fr));
                        gap: 18px;
                    }

                    .kpi-card {
                        padding: 22px;
                        border: 1px solid rgba(108, 186, 255, 0.18);
                        border-radius: 18px;
                        background: rgba(13, 35, 64, 0.82);
                        box-shadow: 0 18px 38px rgba(0, 0, 0, 0.18);
                        transition:
                            transform 0.25s ease,
                            border-color 0.25s ease;
                    }

                    .kpi-card:hover {
                        transform: translateY(-4px);
                        border-color: rgba(69, 221, 255, 0.65);
                    }

                    .kpi-label {
                        color: #9cb2cc;
                        font-size: 13px;
                        letter-spacing: 0.7px;
                        text-transform: uppercase;
                    }

                    .kpi-value {
                        margin-top: 13px;
                        color: #ffffff;
                        font-size: 30px;
                        font-weight: 700;
                    }

                    .kpi-value.warning {
                        color: #ffbb66;
                    }

                    .kpi-value.critical {
                        color: #ff7786;
                    }

                    .kpi-value.positive {
                        color: #62f6c3;
                    }

                    .as-of {
                        margin-top: 24px;
                        color: #7f98b7;
                        font-size: 14px;
                    }

                </style>

            </head>

            <body>

                <main class="container">

                    <header class="header">

                        <div class="brand">
                            Royal Insurance
                        </div>

                        <h1>
                            Portfolio Intelligence Dashboard
                        </h1>

                        <div class="subtitle">
                            Enterprise insurance performance and risk overview
                        </div>

                        <div class="status">
                            Java 21 + Azul Zulu + Spring Boot
                        </div>

                    </header>

                    <h2 class="section-title">
                        Executive Performance
                    </h2>

                    <div id="message" class="message">
                        Loading executive KPIs...
                    </div>

                    <section
                        id="kpiGrid"
                        class="kpi-grid"
                        style="display: none;">
                    </section>

                    <div id="asOf" class="as-of"></div>

                </main>

                <script>

                    function formatCurrency(value) {

                        if (value >= 10000000000) {
                            return "₹" +
                                (value / 10000000000).toFixed(2) +
                                "K Cr";
                        }

                        if (value >= 10000000) {
                            return "₹" +
                                (value / 10000000).toFixed(2) +
                                " Cr";
                        }

                        if (value >= 100000) {
                            return "₹" +
                                (value / 100000).toFixed(2) +
                                " L";
                        }

                        return "₹" +
                            new Intl.NumberFormat("en-IN")
                                .format(value);
                    }

                    function formatNumber(value) {
                        return new Intl.NumberFormat("en-IN")
                            .format(value);
                    }

                    function formatPercent(value) {
                        return (value * 100).toFixed(1) + "%";
                    }

                    function card(label, value, cssClass = "") {

                        return `
                            <article class="kpi-card">
                                <div class="kpi-label">
                                    ${label}
                                </div>

                                <div class="kpi-value ${cssClass}">
                                    ${value}
                                </div>
                            </article>
                        `;
                    }

                    async function loadKpis() {

                        const message =
                            document.getElementById("message");

                        const grid =
                            document.getElementById("kpiGrid");

                        try {

                            const response =
                                await fetch("/api/kpi");

                            const result =
                                await response.json();

                            if (!response.ok) {
                                throw new Error(
                                    result.message ||
                                    "Unable to load KPI data"
                                );
                            }

                            grid.innerHTML = [
                                card(
                                    "Gross Written Premium",
                                    formatCurrency(
                                        result.grossWrittenPremium
                                    )
                                ),

                                card(
                                    "Earned Premium",
                                    formatCurrency(
                                        result.earnedPremium
                                    )
                                ),

                                card(
                                    "Policies in Force",
                                    formatNumber(
                                        result.policiesInForce
                                    )
                                ),

                                card(
                                    "Claims Incurred",
                                    formatCurrency(
                                        result.claimsIncurred
                                    )
                                ),

                                card(
                                    "Loss Ratio",
                                    formatPercent(
                                        result.lossRatio
                                    ),
                                    result.lossRatio > 1
                                        ? "critical"
                                        : "positive"
                                ),

                                card(
                                    "Expense Ratio",
                                    formatPercent(
                                        result.expenseRatio
                                    )
                                ),

                                card(
                                    "Combined Ratio",
                                    formatPercent(
                                        result.combinedRatio
                                    ),
                                    result.combinedRatio > 1
                                        ? "critical"
                                        : "positive"
                                ),

                                card(
                                    "Retention Rate",
                                    formatPercent(
                                        result.retentionRate
                                    ),
                                    "positive"
                                ),

                                card(
                                    "Claims per 1,000 Policies",
                                    Number(
                                        result.claimFrequencyPer1000
                                    ).toFixed(1)
                                )
                            ].join("");

                            message.style.display = "none";
                            grid.style.display = "grid";

                            document.getElementById("asOf")
                                .textContent =
                                "Reporting month: " +
                                result.asOfMonth;

                        } catch (error) {

                            message.classList.add("error");

                            message.textContent =
                                "Dashboard data could not be loaded: " +
                                error.message;
                        }
                    }

                    loadKpis();

                </script>

            </body>

            </html>
            """;
    }

    @GetMapping("/health")
    public Map<String, String> health() {

        Map<String, String> response =
                new LinkedHashMap<>();

        response.put("status", "UP");
        response.put("application", "insurance-dashboard");

        return response;
    }

    @GetMapping("/api/kpi")
    public ResponseEntity<Map<String, Object>> getKpi() {

        try {

            Map<String, Object> kpi =
                    databricksService.getLatestKpi();

            return ResponseEntity.ok(kpi);

        } catch (Exception error) {

            error.printStackTrace();

            Map<String, Object> response =
                    new LinkedHashMap<>();

            response.put(
                    "error",
                    "KPI_QUERY_FAILED"
            );

            response.put(
                    "message",
                    error.getMessage() == null
                            ? "Unknown database error"
                            : error.getMessage()
            );

            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(response);
        }
    }
}