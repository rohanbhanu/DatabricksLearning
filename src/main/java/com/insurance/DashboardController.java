package com.insurance;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api")
public class DashboardController {

    private final DatabricksService service;

    public DashboardController(
            DatabricksService service
    ) {
        this.service = service;
    }


    @GetMapping("/kpi")
    public ResponseEntity<?> kpi() {

        try {
            return ResponseEntity.ok(
                    service.getLatestKpi()
            );
        }
        catch (Exception e) {

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(Map.of(
                            "error",
                            e.getMessage() != null
                                    ? e.getMessage()
                                    : "KPI query failed"
                    ));
        }
    }


    @GetMapping("/trend")
    public ResponseEntity<?> trend() {

        try {
            return ResponseEntity.ok(
                    service.getMonthlyTrend()
            );
        }
        catch (Exception e) {

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(Map.of(
                            "error",
                            e.getMessage() != null
                                    ? e.getMessage()
                                    : "Trend query failed"
                    ));
        }
    }


    @GetMapping("/drilldown")
    public ResponseEntity<?> drilldown(

            @RequestParam(defaultValue = "region")
            String level,

            @RequestParam(required = false)
            String region,

            @RequestParam(required = false)
            String state,

            @RequestParam(required = false)
            String product

    ) {

        try {

            return ResponseEntity.ok(
                    service.getDrilldown(
                            level,
                            region,
                            state,
                            product
                    )
            );

        }
        catch (Exception e) {

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(Map.of(
                            "error",
                            e.getMessage() != null
                                    ? e.getMessage()
                                    : "Drilldown query failed"
                    ));
        }
    }


    @GetMapping("/claims")
    public ResponseEntity<?> claims() {

        try {

            return ResponseEntity.ok(
                    service.getClaimsSummary()
            );

        }
        catch (Exception e) {

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(Map.of(
                            "error",
                            e.getMessage() != null
                                    ? e.getMessage()
                                    : "Claims query failed"
                    ));
        }
    }


    @GetMapping("/claim-risk")
    public ResponseEntity<?> claimRisk() {

        try {

            return ResponseEntity.ok(
                    service.getClaimRiskSummary()
            );

        }
        catch (Exception e) {

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(Map.of(
                            "error",
                            e.getMessage() != null
                                    ? e.getMessage()
                                    : "Claim risk query failed"
                    ));
        }
    }


    @GetMapping("/health")
    public Map<String, String> health() {

        return Map.of(
                "status", "UP",
                "application",
                "Royal Insurance Portfolio Intelligence"
        );
    }
}