package com.insurance;

import org.springframework.stereotype.Service;

import java.sql.*;
import java.util.*;

@Service
public class DatabricksService {

    private static final String HOST =
            "dbc-a5e0c9f5-8a51.cloud.databricks.com";

    private static final String HTTP_PATH =
            "/sql/1.0/warehouses/20a98227c8517949";

    private Connection getConnection() throws Exception {

        String clientId =
                System.getenv("DATABRICKS_CLIENT_ID");

        String clientSecret =
                System.getenv("DATABRICKS_CLIENT_SECRET");

        if (clientId == null || clientSecret == null) {
            throw new IllegalStateException(
                    "Databricks OAuth environment variables are missing."
            );
        }

        String url =
                "jdbc:databricks://" +
                HOST +
                ":443";

        Properties p = new Properties();

        p.put("httpPath", HTTP_PATH);
        p.put("AuthMech", "11");
        p.put("Auth_Flow", "1");
        p.put("OAuth2ClientId", clientId);
        p.put("OAuth2Secret", clientSecret);

        p.put("ConnCatalog", "royalinsurance");
        p.put("ConnSchema", "edw");

        return DriverManager.getConnection(url, p);
    }


    // =====================================================
    // EXECUTIVE KPI
    // =====================================================

    public Map<String, Object> getLatestKpi()
            throws Exception {

        String sql = """
            SELECT *
            FROM royalinsurance.edw.executive_kpi
            ORDER BY as_of_month DESC
            LIMIT 1
            """;

        Map<String, Object> result =
                new LinkedHashMap<>();

        try (
                Connection connection = getConnection();
                Statement statement =
                        connection.createStatement();
                ResultSet rs =
                        statement.executeQuery(sql)
        ) {

            if (rs.next()) {

                result.put(
                        "asOfMonth",
                        rs.getDate("as_of_month").toString()
                );

                result.put(
                        "grossWrittenPremium",
                        rs.getLong(
                                "gross_written_premium_inr"
                        )
                );

                result.put(
                        "earnedPremium",
                        rs.getLong(
                                "earned_premium_inr"
                        )
                );

                result.put(
                        "policiesInForce",
                        rs.getLong(
                                "policies_in_force"
                        )
                );

                result.put(
                        "claimsIncurred",
                        rs.getLong(
                                "claims_incurred_inr"
                        )
                );

                result.put(
                        "lossRatio",
                        rs.getDouble("loss_ratio")
                );

                result.put(
                        "expenseRatio",
                        rs.getDouble("expense_ratio")
                );

                result.put(
                        "combinedRatio",
                        rs.getDouble("combined_ratio")
                );

                result.put(
                        "retentionRate",
                        rs.getDouble("retention_rate")
                );

                result.put(
                        "claimFrequency",
                        rs.getDouble(
                                "claim_frequency_per_1000"
                        )
                );
            }
        }

        return result;
    }


    // =====================================================
    // MONTHLY TREND
    // =====================================================

    public List<Map<String, Object>>
    getMonthlyTrend() throws Exception {

        String sql = """
            SELECT
                month,
                SUM(gross_written_premium_inr) AS gwp,
                SUM(earned_premium_inr) AS earned,
                SUM(claims_incurred_inr) AS claims,
                SUM(policies_in_force) AS policies,
                CASE
                    WHEN SUM(earned_premium_inr) = 0
                    THEN 0
                    ELSE
                        SUM(claims_incurred_inr)
                        / SUM(earned_premium_inr)
                END AS loss_ratio
            FROM royalinsurance.edw.portfolio_monthly
            GROUP BY month
            ORDER BY month
            """;

        return query(sql);
    }


    // =====================================================
    // DRILL DOWN
    //
    // region -> state -> product -> channel
    // =====================================================

    public List<Map<String, Object>>
    getDrilldown(
            String level,
            String region,
            String state,
            String product
    ) throws Exception {

        Set<String> allowed =
                Set.of(
                        "region",
                        "state",
                        "product",
                        "channel"
                );

        if (!allowed.contains(level)) {
            throw new IllegalArgumentException(
                    "Invalid drill level"
            );
        }

        StringBuilder sql =
                new StringBuilder("""
                SELECT
                """);

        sql.append(level);

        sql.append(" AS category, ");

        sql.append("""
                SUM(gross_written_premium_inr)
                AS premium,

                SUM(claims_incurred_inr)
                AS claims,

                SUM(policies_in_force)
                AS policies,

                CASE
                WHEN SUM(earned_premium_inr) = 0
                THEN 0
                ELSE
                        SUM(claims_incurred_inr)
                        / SUM(earned_premium_inr)
                END AS loss_ratio

                FROM royalinsurance.edw.portfolio_monthly
                WHERE 1=1
                """);
        List<Object> params =
                new ArrayList<>();

        if (region != null && !region.isBlank()) {
            sql.append(" AND region = ?");
            params.add(region);
        }

        if (state != null && !state.isBlank()) {
            sql.append(" AND state = ?");
            params.add(state);
        }

        if (product != null && !product.isBlank()) {
            sql.append(" AND product = ?");
            params.add(product);
        }

        sql.append(
                " GROUP BY " +
                level +
                " ORDER BY premium DESC"
        );

        return preparedQuery(
                sql.toString(),
                params
        );
    }


    // =====================================================
    // CLAIM STATUS
    // =====================================================

    public List<Map<String, Object>>
    getClaimsSummary() throws Exception {

        String sql = """
            SELECT
                claim_status,
                COUNT(*) AS claim_count,
                SUM(claim_amount_inr) AS claim_amount,
                SUM(paid_amount_inr) AS paid_amount,
                SUM(outstanding_amount_inr) AS outstanding_amount,
                AVG(settlement_days) AS avg_settlement_days,
                AVG(fraud_risk_score) AS avg_fraud_risk
            FROM royalinsurance.edw.claims
            GROUP BY claim_status
            ORDER BY claim_count DESC
            """;

        return query(sql);
    }


    // =====================================================
    // CLAIM RISK SUMMARY
    // =====================================================

    public Map<String, Object>
    getClaimRiskSummary() throws Exception {

        String sql = """
            SELECT
                COUNT(*) AS total_claims,

                SUM(
                    CASE
                        WHEN sla_breach_flag = 'Y'
                        THEN 1 ELSE 0
                    END
                ) AS sla_breaches,

                AVG(fraud_risk_score)
                    AS avg_fraud_score,

                AVG(settlement_days)
                    AS avg_settlement_days,

                SUM(outstanding_amount_inr)
                    AS outstanding_amount

            FROM royalinsurance.edw.claims
            """;

        List<Map<String, Object>> data =
                query(sql);

        if (data.isEmpty()) {
            return new LinkedHashMap<>();
        }

        return data.get(0);
    }


    // =====================================================
    // GENERIC QUERY
    // =====================================================

    private List<Map<String, Object>>
    query(String sql) throws Exception {

        List<Map<String, Object>> rows =
                new ArrayList<>();

        try (
                Connection connection = getConnection();
                Statement statement =
                        connection.createStatement();
                ResultSet rs =
                        statement.executeQuery(sql)
        ) {

            ResultSetMetaData meta =
                    rs.getMetaData();

            int columns =
                    meta.getColumnCount();

            while (rs.next()) {

                Map<String, Object> row =
                        new LinkedHashMap<>();

                for (int i = 1; i <= columns; i++) {

                    Object value =
                            rs.getObject(i);

                    if (value instanceof java.sql.Date
                        || value instanceof java.sql.Timestamp
                        || value instanceof java.sql.Time) {
                    value = value.toString();
                }

                    row.put(
                            meta.getColumnLabel(i),
                            value
                    );
                }

                rows.add(row);
            }
        }

        return rows;
    }


    private List<Map<String, Object>>
    preparedQuery(
            String sql,
            List<Object> params
    ) throws Exception {

        List<Map<String, Object>> rows =
                new ArrayList<>();

        try (
                Connection connection = getConnection();
                PreparedStatement statement =
                        connection.prepareStatement(sql)
        ) {

            for (int i = 0; i < params.size(); i++) {
                statement.setObject(
                        i + 1,
                        params.get(i)
                );
            }

            try (
                    ResultSet rs =
                            statement.executeQuery()
            ) {

                ResultSetMetaData meta =
                        rs.getMetaData();

                int columns =
                        meta.getColumnCount();

                while (rs.next()) {

                    Map<String, Object> row =
                            new LinkedHashMap<>();

                    for (
                            int i = 1;
                            i <= columns;
                            i++
                    ) {

                        row.put(
                                meta.getColumnLabel(i),
                                rs.getObject(i)
                        );
                    }

                    rows.add(row);
                }
            }
        }

        return rows;
    }
}