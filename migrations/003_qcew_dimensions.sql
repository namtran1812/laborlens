ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS aggregation_level_code UInt8
        AFTER ownership_code;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS size_code UInt8
        AFTER aggregation_level_code;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS disclosure_code LowCardinality(String)
        AFTER quarter;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS taxable_quarterly_wages Nullable(Float64)
        AFTER total_quarterly_wages;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS quarterly_contributions Nullable(Float64)
        AFTER taxable_quarterly_wages;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS lq_disclosure_code LowCardinality(String)
        AFTER average_weekly_wage;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS establishment_location_quotient Nullable(Float64)
        AFTER lq_disclosure_code;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS month1_employment_location_quotient Nullable(Float64)
        AFTER establishment_location_quotient;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS month2_employment_location_quotient Nullable(Float64)
        AFTER month1_employment_location_quotient;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS total_wage_location_quotient Nullable(Float64)
        AFTER employment_location_quotient;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_disclosure_code LowCardinality(String)
        AFTER wage_location_quotient;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_establishments_change Nullable(Int64)
        AFTER oty_disclosure_code;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_establishments_pct_change Nullable(Float64)
        AFTER oty_establishments_change;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_month3_employment_change Nullable(Int64)
        AFTER oty_establishments_pct_change;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_month3_employment_pct_change Nullable(Float64)
        AFTER oty_month3_employment_change;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_total_quarterly_wages_change Nullable(Int64)
        AFTER oty_month3_employment_pct_change;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_total_quarterly_wages_pct_change Nullable(Float64)
        AFTER oty_total_quarterly_wages_change;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_average_weekly_wage_change Nullable(Int64)
        AFTER oty_total_quarterly_wages_pct_change;

ALTER TABLE laborlens.qcew_observations
    ADD COLUMN IF NOT EXISTS oty_average_weekly_wage_pct_change Nullable(Float64)
        AFTER oty_average_weekly_wage_change;
