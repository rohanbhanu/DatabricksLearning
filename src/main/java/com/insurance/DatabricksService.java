package com.insurance;

import org.springframework.stereotype.Service;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Properties;

@Service
public class DatabricksService {

    private static final String SERVER_HOSTNAME =
            "dbc-a5e0c9f5-8a51.cloud.databricks.com";

    private static final String HTTP_PATH =
            "/sql/1.0/warehouses/20a98227c8517949";

    private static final String KPI_SQL = """
            SELECT
                as_of_month,
                gross_written_premium_inr,
                earned_premium_inr,
                policies_in_force,
                claims_incurred_inr,
                loss_ratio,
                expense_ratio,
                combined_ratio,
                retention_rate,
                claim_frequency_per_1000
            FROM royalinsurance.edw.executive_kpi
            ORDER BY as_of_month DESC
            LIMIT 1
            """;

    private Connection getConnection() throws Exception {

        String clientId = System.getenv("DATABRICKS_CLIENT_ID");
        String clientSecret = System.getenv("DATABRICKS_CLIENT_SECRET");

        if (clientId == null || clientId.isBlank()) {
            throw new IllegalStateException(
                    "DATABRICKS_CLIENT_ID environment variable is missing"
            );
        }

        if (clientSecret == null || clientSecret.isBlank()) {
            throw new IllegalStateException(
                    "DATABRICKS_CLIENT_SECRET environment variable is missing"
            );
        }

        String jdbcUrl =
                "jdbc:databricks://" + SERVER_HOSTNAME + ":443";

        Properties properties = new Properties();

        properties.put("httpPath", HTTP_PATH);
        properties.put("AuthMech", "11");
        properties.put("Auth_Flow", "1");
        properties.put("OAuth2ClientId", clientId);
        properties.put("OAuth2Secret", clientSecret);

        properties.put("ConnCatalog", "royalinsurance");
        properties.put("ConnSchema", "edw");

        return DriverManager.getConnection(
                jdbcUrl,
                properties
        );
    }

    public Map<String, Object> getLatestKpi() throws Exception {

        Map<String, Object> kpi = new LinkedHashMap<>();

        try (
                Connection connection = getConnection();
                Statement statement = connection.createStatement();
                ResultSet resultSet = statement.executeQuery(KPI_SQL)
        ) {

            if (!resultSet.next()) {
                throw new IllegalStateException(
                        "No records found in royalinsurance.edw.executive_kpi"
                );
            }

            kpi.put(
                    "asOfMonth",
                    resultSet.getDate("as_of_month").toString()
            );

            kpi.put(
                    "grossWrittenPremium",
                    resultSet.getLong("gross_written_premium_inr")
            );

            kpi.put(
                    "earnedPremium",
                    resultSet.getLong("earned_premium_inr")
            );

            kpi.put(
                    "policiesInForce",
                    resultSet.getLong("policies_in_force")
            );

            kpi.put(
                    "claimsIncurred",
                    resultSet.getLong("claims_incurred_inr")
            );

            kpi.put(
                    "lossRatio",
                    resultSet.getDouble("loss_ratio")
            );

            kpi.put(
                    "expenseRatio",
                    resultSet.getDouble("expense_ratio")
            );

            kpi.put(
                    "combinedRatio",
                    resultSet.getDouble("combined_ratio")
            );

            kpi.put(
                    "retentionRate",
                    resultSet.getDouble("retention_rate")
            );

            kpi.put(
                    "claimFrequencyPer1000",
                    resultSet.getDouble(
                            "claim_frequency_per_1000"
                    )
            );
        }

        return kpi;
    }
}