from laborlens.data.qcew import QcewClient


def test_qcew_quarterly_url():
    assert QcewClient.quarterly_url(
        2024,
        2,
    ).endswith("/2024/csv/2024_qtrly_singlefile.zip")


def test_qcew_rejects_invalid_quarter():
    try:
        QcewClient.quarterly_url(
            2024,
            5,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_qcew_parse_csv():
    content = """area_fips,own_code,industry_code,year,qtr,area_title,industry_title,qtrly_estabs,month1_emplvl,month2_emplvl,month3_emplvl,total_qtrly_wages,avg_wkly_wage,lq_month3_emplvl,lq_avg_wkly_wage
"12000","5","10","2024","2","Florida -- Statewide","10 Total, all industries","100","1000","1010","1020","12345678","931","1.02","0.97"
"""

    rows = QcewClient.parse_csv(content)

    assert len(rows) == 1

    row = rows[0]

    assert row.area_fips == "12000"
    assert row.industry_code == "10"
    assert row.year == 2024
    assert row.quarter == 2
    assert row.month3_employment == 1020
    assert row.average_weekly_wage == 931.0
    assert row.employment_location_quotient == 1.02


def test_qcew_streaming_row_tuple():
    from datetime import UTC, datetime

    from laborlens.services.qcew_ingestion import (
        QcewIngestionService,
    )

    row = {
        "area_fips": "01000",
        "own_code": "0",
        "industry_code": "10",
        "agglvl_code": "50",
        "size_code": "0",
        "year": "2024",
        "qtr": "2",
        "disclosure_code": "",
        "qtrly_estabs": "160692",
        "month1_emplvl": "2103439",
        "month2_emplvl": "2110214",
        "month3_emplvl": "2116266",
        "total_qtrly_wages": "31539244619",
        "taxable_qtrly_wages": "2459224769",
        "qtrly_contributions": "14061511",
        "avg_wkly_wage": "1150",
        "lq_disclosure_code": "",
        "lq_qtrly_estabs": "1.00",
        "lq_month1_emplvl": "1.00",
        "lq_month2_emplvl": "1.00",
        "lq_month3_emplvl": "1.00",
        "lq_total_qtrly_wages": "1.00",
        "lq_avg_wkly_wage": "1.00",
        "oty_disclosure_code": "",
        "oty_qtrly_estabs_chg": "4568",
        "oty_qtrly_estabs_pct_chg": "2.9",
        "oty_month3_emplvl_chg": "31082",
        "oty_month3_emplvl_pct_chg": "1.5",
        "oty_total_qtrly_wages_chg": "1684016507",
        "oty_total_qtrly_wages_pct_chg": "5.6",
        "oty_avg_wkly_wage_chg": "43",
        "oty_avg_wkly_wage_pct_chg": "3.9",
    }

    now = datetime.now(UTC)

    result = QcewIngestionService._row_tuple(
        row,
        now,
    )

    assert result[0] == "01000"
    assert result[1] == "10"
    assert result[3] == 50
    assert result[6] == 2
    assert result[11] == 2_116_266
    assert result[27] == 1.5
