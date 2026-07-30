from app.services.nl_query_service import rule_based_parse

def test_housing_krishna_above_90():
    result = rule_based_parse("Show pending housing applications in Krishna district above 90 days")
    assert result["intent"] == "scheme_status"
    assert result["filters"]["district"] == "Krishna"
    assert result["filters"]["scheme_type"] == "housing"
    assert result["filters"]["min_pending_days"] == 90

def test_anomaly_query():
    result = rule_based_parse("Which departments have anomalies?")
    assert result["intent"] == "anomaly_check"

def test_pension_query():
    result = rule_based_parse("Show pension scheme status in Guntur")
    assert result["intent"] == "scheme_status"
    assert result["filters"]["district"] == "Guntur"
    assert result["filters"]["scheme_type"] == "pension"

def test_department_spending():
    result = rule_based_parse("Show infrastructure department spending")
    assert result["intent"] in ("department_kpi", "scheme_status")

def test_summary_query():
    result = rule_based_parse("Give me an overview of the dashboard")
    assert result["intent"] == "summary"

def test_day_threshold_extraction():
    result = rule_based_parse("pending applications more than 45 days")
    assert result["filters"].get("min_pending_days") == 45
