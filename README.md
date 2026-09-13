# industrial-rework-optimization-pipeline
An end-to-end cloud data engineering pipeline designed to track, analyze, and minimize rework inventory in manufacturing, applying Lean and continuous improvement principles to physical plant operations.

## Business Problem
Formulation variations (e.g., Freezing Point Depression deviations) and mechanical issues (excessive foaming in mixing tanks) generate process bottlenecks and high rework volumes. This ties up working capital and physical plant capacity.

**The Solution:** This project simulates a real-time ingestion and analytics architecture to evaluate manufacturing efficiency using **Return on Space-Time (RoST)** metrics, transforming physical sensor data into actionable financial insights.

## Cloud Architecture & Tech Stack
This repository demonstrates a modern data stack transition from raw plant data to a Data Warehouse:
* **Data Generation & Ingestion (Mocked Cloud):** `Python` (pandas, numpy) simulating IoT sensors and ERP logs, built to integrate with AWS S3 / Azure Data Lake.
* **Big Data Processing (ETL):** `Databricks` / `PySpark` for massive data cleaning, mass balance calculations, and Delta Lake storage.
* **Data Modeling & Analytics:** `Snowflake` / `Advanced SQL` (CTEs, Window Functions) to build a Kimball Star Schema and compute running financial impacts.

## Repository Structure

1. `/data_simulation`
   * `generate_factory_data.py`: Python script simulating 90 days of continuous manufacturing data (temperatures, foam levels, rework kg) with built-in business logic for quality deviations.

2. `/databricks_etl`
   * `transform_production_data.py`: PySpark pipeline that ingests raw data, casts data types, applies quality control rules, and uses Window Functions to calculate rolling rework averages per production line.

3. `/snowflake_sql`
   * `01_star_schema_and_analytics.sql`: Snowflake SQL script establishing the analytical Data Warehouse. Includes dimensional modeling (Star Schema) and advanced analytical views calculating cumulative financial loss and RoST impact categories.

## Key Technical Skills Highlighted
* Distributed data processing with PySpark.
* Cloud Data Warehousing and analytical modeling in Snowflake.
* Translation of complex physical chemistry and engineering processes into data architecture.
