from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("Dairy_Base_Rework_ETL") \
    .getOrCreate()


def clean_and_enrich_production(input_path: str, output_path: str):
    raw_df = spark.read.csv(input_path, header=True, inferSchema=True)

    base_df = raw_df \
        .withColumn("Timestamp", F.to_timestamp("Timestamp")) \
        .withColumn("Mix_Temperature_C", F.col("Mix_Temperature_C").cast("double")) \
        .withColumn("FP_Depression_C", F.col("FP_Depression_C").cast("double")) \
        .withColumn("Foam_Level_Pct", F.col("Foam_Level_Pct").cast("double")) \
        .withColumn("Rework_Volume_kg", F.col("Rework_Volume_kg").cast("double"))

    # Identify deviations
    status_df = base_df.withColumn(
        "Quality_Status",
        F.when((F.col("FP_Depression_C") < -2.8) | (F.col("FP_Depression_C") > -2.0), "FPD_Out_Of_Spec")
         .when(F.col("Mix_Temperature_C") > 75.0, "Overheated")
         .when(F.col("Foam_Level_Pct") > 12.0, "High_Foam_Risk")
         .otherwise("In_Spec")
    )

    # Analysis with moving average
    # Detect accumulation of rework problems
    line_window = Window.partitionBy("Line").orderBy("Timestamp").rowsBetween(-2, 0)

    enriched_df = status_df \
        .withColumn("Rolling_Rework_Avg_kg", F.round(F.avg("Rework_Volume_kg").over(line_window), 2)) \
        .withColumn(
            "Requires_Operator_Intervention",
            F.when((F.col("Rolling_Rework_Avg_kg") > 400) & (F.col("Quality_Status") != "In_Spec"), True)
             .otherwise(False)
        )
  
    final_df = enriched_df \
        .withColumn("ETL_Processed_At", F.current_timestamp())

    final_df.write.mode("overwrite").format("delta").save(output_path)
    print(f"[SUCCESS] Processed {final_df.count()} batch records.")


if __name__ == "__main__":
    RAW_DATA_PATH = "dbfs:/mnt/raw_data/raw_production_data.csv"
    PROCESSED_DATA_PATH = "dbfs:/mnt/processed/rework_analytics_delta"

    clean_and_enrich_production(RAW_DATA_PATH, PROCESSED_DATA_PATH)
