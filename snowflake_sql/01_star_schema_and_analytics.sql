create or replace database manufacturing_analytics;
use database manufacturing_analytics;

create or replace schema rework_optimization;
use schema rework_optimization;

--Dimensions
--Dimension Product lines
create or replace table dim_product_line (
    line_id int autoincrement primary key,
    line_code varchar(20) not null unique,
    plant_location varchar(50),
    designed_capacity_lph numeric(10,2)
);

--Dimension Quality status
create or replace table dim_quality_status (
    quality_status_id int autoincrement primary key,
    quality_status_code varchar(30) not null unique,
    status_description varchar(100),
    requires_action boolean default false
);

-- Fact table
create or replace table fact_production_batches (
    batch_sk int autoincrement primary key,
    batch_id varchar(50) not null,
    timestamp timestamp_ntz not null,
    line_id int foreign key references dim_product_line(line_id),
    quality_status_id int foreign key references dim_quality_status(quality_status_id),
    mix_temperature_c numeric(5,2),
    fp_depression_c numeric(5,2),
    foam_level_pct numeric(5,2),
    rework_volume_kg numeric(10,2),
    etl_loaded_at timestamp_ntz default current_timestamp()
);

insert into dim_product_line (line_code, plant_location, designed_capacity_lph)
values 
    ('Line_A', 'Simcoe Plant', 5000.00),
    ('Line_B', 'Simcoe Plant', 5000.00),
    ('Line_C', 'Simcoe Plant', 5000.00);

insert into dim_quality_status (quality_status_code, status_description, requires_action)
values 
    ('In_Spec', 'Batch meets all chemical & physical specs', false),
    ('FPD_Out_Of_Spec', 'Freezing Point Depression deviation', true),
    ('Overheated', 'Pasteurization temp exceeded threshold', true),
    ('High_Foam_Risk', 'Foam level creates volume overflow risk', true);

--Analysis
create or replace view v_rework_financial_impact_analysis as
with batch_metrics as (
    select 
        f.batch_id,
        l.line_code,
        f.timestamp,
        f.mix_temperature_c,
        f.fp_depression_c,
        f.foam_level_pct,
        f.rework_volume_kg,
        q.quality_status_code,
        q.requires_action,
        -- Standard blend rework cost ($2.45/kg impact)
        round(f.rework_volume_kg * 2.45, 2) as estimated_rework_cost_usd
    from fact_production_batches f
    join dim_product_line l on f.line_id = l.line_id
    join dim_quality_status q on f.quality_status_id = q.quality_status_id
),
rolling_line_analytics as (
  --Detect tendencies and accumulations
    select 
        batch_id,
        line_code,
        timestamp,
        quality_status_code,
        rework_volume_kg,
        estimated_rework_cost_usd,
        round(avg(rework_volume_kg) over (
            partition by line_code 
            order by timestamp 
            rows between 4 preceding and current row
        ), 2) as rolling_5batch_avg_rework_kg,
        sum(estimated_rework_cost_usd) over (
            partition by line_code 
            order by timestamp
        ) as cumulative_rework_cost_usd,
        dense_rank() over (
            partition by line_code 
            order by estimated_rework_cost_usd desc
        ) as rework_cost_rank_in_line
    from batch_metrics
)
select 
    batch_id,
    line_code,
    timestamp,
    quality_status_code,
    rework_volume_kg,
    estimated_rework_cost_usd,
    rolling_5batch_avg_rework_kg,
    cumulative_rework_cost_usd,
    rework_cost_rank_in_line,
  --Impact RoST (Return on Space-time)
    case 
        when rolling_5batch_avg_rework_kg > 400.00 then 'HIGH_ROST_PENALTY'
        when rolling_5batch_avg_rework_kg between 150.00 and 400.00 then 'MODERATE_ROST_IMPACT'
        else 'OPTIMAL_SPACE_TIME_EFFICIENCY'
    end as rost_storage_impact_category
from rolling_line_analytics
order by line_code, timestamp;
