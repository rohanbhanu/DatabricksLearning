# India Omnichannel Retail Lakehouse Dataset

Synthetic learning dataset for Databricks Auto Loader, Lakeflow Spark Declarative Pipelines, AI/BI dashboards, and Genie spaces.

## Landing pattern
Upload `sales_transactions_batch_01.csv` first, then batches 02-10 incrementally. Batches 09-10 add `device_type` and `coupon_code` to exercise schema evolution.

## Suggested medallion outputs
- Bronze: raw sales plus `_metadata.file_name`, ingestion time, rescued data.
- Silver: typed, deduplicated, standardized sales joined to customer/product/store/campaign dimensions; quarantine invalid rows.
- Gold: daily_sales_kpi, product_performance, customer_360, regional_sales, channel_performance, campaign_roi, returns_analysis.

## Useful transformations
cast, to_timestamp, to_date, trim, upper/initcap, coalesce, when/otherwise, regexp_replace, split, concat_ws, date_format, datediff, round, greatest/least, dropDuplicates, explode if you create arrays, joins, window functions, groupBy/agg, pivot, rank, lag, rolling averages.

## Suggested calculated measures
Gross sales = quantity * unit_price
Discount amount = gross sales * discount_pct
Net sales = gross sales - discount amount
Tax amount = net sales * tax_pct
Order value = net sales + tax amount + shipping_fee
Gross profit = net sales - quantity * unit_cost

## Genie questions
1. What were net sales and gross profit by month and region?
2. Which five subcategories have the highest return rate?
3. Compare average order value for loyalty and non-loyalty customers.
4. Which campaign produced the highest sales relative to budget?
5. Show a 7-day moving average of daily revenue.
6. Which customers are high value but have not purchased in 60 days?
7. Explain the sales decline by channel for the latest complete month.
