CREATE TABLE IF NOT EXISTS laborlens.qcew_industries
(
    industry_code String,
    industry_title String,
    naics_version UInt16,
    source LowCardinality(String),
    ingested_at DateTime64(3, 'UTC')
        DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY
(
    naics_version,
    industry_code
);


CREATE TABLE IF NOT EXISTS laborlens.qcew_areas
(
    area_fips String,
    area_title String,
    source LowCardinality(String),
    ingested_at DateTime64(3, 'UTC')
        DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY area_fips;
