import pytest

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_seed_and_summary(client):
    r = await client.post("/api/v1/analytics/seed")
    assert r.status_code == 200
    r = await client.get("/api/v1/analytics/executive-summary")
    assert r.status_code == 200
    data = r.json()
    assert "departments" in data
    assert "schemes" in data
    assert data["departments"]["total"] > 0

@pytest.mark.asyncio
async def test_list_departments(client):
    r = await client.get("/api/v1/departments/")
    assert r.status_code == 200
    depts = r.json()
    assert isinstance(depts, list)
    assert len(depts) > 0

@pytest.mark.asyncio
async def test_list_schemes_filtered(client):
    r = await client.get("/api/v1/schemes/?district=Krishna")
    assert r.status_code == 200
    schemes = r.json()
    assert all(s["district"] == "Krishna" for s in schemes)

@pytest.mark.asyncio
async def test_nl_query_no_claude(client):
    r = await client.post("/api/v1/query/", json={"query": "Show pending housing applications in Krishna district above 90 days"})
    assert r.status_code == 200
    data = r.json()
    assert "result_summary" in data
    assert data["parsed_intent"] is not None

@pytest.mark.asyncio
async def test_anomaly_detection(client):
    r = await client.post("/api/v1/departments/run-anomaly-detection")
    assert r.status_code == 200
    data = r.json()
    assert "anomalies_found" in data

@pytest.mark.asyncio
async def test_district_stats(client):
    r = await client.get("/api/v1/analytics/district-stats")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.asyncio
async def test_delayed_schemes(client):
    r = await client.get("/api/v1/schemes/?is_delayed=true")
    assert r.status_code == 200
    schemes = r.json()
    assert all(s["is_delayed"] for s in schemes)
