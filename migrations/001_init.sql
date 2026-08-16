CREATE DATABASE IF NOT EXISTS laborlens;


CREATE TABLE IF NOT EXISTS laborlens.series
(
    series_id String,

    title String,

    frequency LowCardinality(String),

    units String,

    seasonal_adjustment String,

    observation_start Date32,

    observation_end Date32,

    last_updated String,

    notes String,

    source LowCardinality(String),

    ingested_at DateTime64(3, 'UTC')
        DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY series_id;


CREATE TABLE IF NOT EXISTS laborlens.observations
(
    series_id String,

    observation_date Date,

    value Nullable(Float64),

    realtime_start Date,

    realtime_end Date,

    source LowCardinality(String),

    ingested_at DateTime64(3, 'UTC')
        DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
PARTITION BY toYear(observation_date)
ORDER BY
(
    series_id,
    observation_date,
    realtime_start,
    realtime_end
);


CREATE TABLE IF NOT EXISTS laborlens.ingestion_runs
(
    run_id UUID,

    series_id String,

    mode LowCardinality(String),

    started_at DateTime64(3, 'UTC'),

    finished_at Nullable(
        DateTime64(3, 'UTC')
    ),

    row_count UInt64,

    status LowCardinality(String),

    error Nullable(String)
)
ENGINE = MergeTree
ORDER BY
(
    started_at,
    run_id
);
