CREATE TABLE IF NOT EXISTS laborlens.qcew_observations
(
    area_fips String,

    industry_code String,

    ownership_code UInt8,

    year UInt16,

    quarter UInt8,

    establishments Nullable(UInt64),

    month1_employment Nullable(UInt64),

    month2_employment Nullable(UInt64),

    month3_employment Nullable(UInt64),

    total_quarterly_wages Nullable(Float64),

    average_weekly_wage Nullable(Float64),

    employment_location_quotient Nullable(Float64),

    wage_location_quotient Nullable(Float64),

    area_title LowCardinality(String),

    industry_title String,

    source LowCardinality(String)
        DEFAULT 'BLS_QCEW',

    ingested_at DateTime64(3, 'UTC')
        DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
PARTITION BY year
ORDER BY
(
    year,
    quarter,
    area_fips,
    ownership_code,
    industry_code
);
