-- 1. Cumulative Rework Cost Impact ($ USD)
Cumulative Rework Cost = 
CALCULATE(
    SUM('fact_production_batches'[estimated_rework_cost_usd]),
    FILTER(
        ALLSELECTED('fact_production_batches'[timestamp]),
        'fact_production_batches'[timestamp] <= MAX('fact_production_batches'[timestamp])
    )
)

-- 2. Rolling 5-Batch Rework Moving Average (kg)
Rolling 5Batch Avg Rework = 
CALCULATE(
    AVERAGE('fact_production_batches'[rework_volume_kg]),
    DATESINPERIOD(
        'fact_production_batches'[timestamp],
        LASTDATE('fact_production_batches'[timestamp]),
        -5,
        DAY
    )
)

-- 3. Dynamic RoST Storage Penalty Classification
RoST Penalty Category = 
VAR AvgRework = [Rolling 5Batch Avg Rework]
RETURN
    SWITCH(
        TRUE(),
        AvgRework > 400, "HIGH_ROST_PENALTY",
        AvgRework >= 150, "MODERATE_ROST_IMPACT",
        "OPTIMAL_SPACE_TIME_EFFICIENCY"
    )
