from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.models.department import Department
from app.models.scheme import Scheme
from app.models.kpi_metric import KpiMetric

AP_DEPARTMENTS = [
    {"name": "Social Welfare & Tribal Welfare", "code": "SWTW", "category": "welfare", "budget_crores": 8500, "spent_crores": 7200, "pending_files": 234, "avg_file_clearance_days": 18},
    {"name": "Roads & Buildings", "code": "RB", "category": "infrastructure", "budget_crores": 15000, "spent_crores": 14800, "pending_files": 89, "avg_file_clearance_days": 22},
    {"name": "Finance Department", "code": "FIN", "category": "finance", "budget_crores": 5000, "spent_crores": 250, "pending_files": 45, "avg_file_clearance_days": 8},
    {"name": "Health, Medical & Family Welfare", "code": "HMFW", "category": "health", "budget_crores": 12000, "spent_crores": 10800, "pending_files": 567, "avg_file_clearance_days": 52},
    {"name": "Agriculture & Cooperation", "code": "AGR", "category": "welfare", "budget_crores": 9000, "spent_crores": 8100, "pending_files": 312, "avg_file_clearance_days": 28},
    {"name": "Education Department", "code": "EDU", "category": "education", "budget_crores": 18000, "spent_crores": 16200, "pending_files": 128, "avg_file_clearance_days": 15},
    {"name": "Revenue Department", "code": "REV", "category": "revenue", "budget_crores": 3000, "spent_crores": 2700, "pending_files": 890, "avg_file_clearance_days": 61},
    {"name": "Municipal Administration & Urban Development", "code": "MAUD", "category": "infrastructure", "budget_crores": 11000, "spent_crores": 9900, "pending_files": 445, "avg_file_clearance_days": 35},
]

AP_SCHEMES = [
    # Welfare schemes
    {"name": "YSR Pension Kanuka", "scheme_type": "pension", "district": "Krishna", "total_beneficiaries": 285000, "active_beneficiaries": 278000, "pending_applications": 1240, "avg_pending_days": 18, "sla_days": 21, "disbursed_crores": 890, "target_crores": 950, "completion_pct": 93.7, "is_delayed": False},
    {"name": "YSR Pension Kanuka", "scheme_type": "pension", "district": "Guntur", "total_beneficiaries": 310000, "active_beneficiaries": 298000, "pending_applications": 2100, "avg_pending_days": 35, "sla_days": 21, "disbursed_crores": 820, "target_crores": 940, "completion_pct": 87.2, "is_delayed": True, "delay_reason": "Aadhar verification delays"},
    {"name": "YSR Pension Kanuka", "scheme_type": "pension", "district": "East Godavari", "total_beneficiaries": 195000, "active_beneficiaries": 189000, "pending_applications": 890, "avg_pending_days": 22, "sla_days": 21, "disbursed_crores": 560, "target_crores": 610, "completion_pct": 91.8, "is_delayed": True, "delay_reason": "Recent enrollment surge"},
    # Housing schemes
    {"name": "PMAY-G Housing", "scheme_type": "housing", "district": "Krishna", "total_beneficiaries": 45000, "active_beneficiaries": 38000, "pending_applications": 3200, "avg_pending_days": 95, "sla_days": 30, "disbursed_crores": 480, "target_crores": 650, "completion_pct": 73.8, "is_delayed": True, "delay_reason": "Material shortage and contractor delays"},
    {"name": "PMAY-G Housing", "scheme_type": "housing", "district": "Kurnool", "total_beneficiaries": 38000, "active_beneficiaries": 31000, "pending_applications": 4100, "avg_pending_days": 112, "sla_days": 30, "disbursed_crores": 380, "target_crores": 600, "completion_pct": 63.3, "is_delayed": True, "delay_reason": "Ground report delays and beneficiary verification backlog"},
    {"name": "PMAY-G Housing", "scheme_type": "housing", "district": "Anantapur", "total_beneficiaries": 52000, "active_beneficiaries": 45000, "pending_applications": 2800, "avg_pending_days": 78, "sla_days": 30, "disbursed_crores": 620, "target_crores": 750, "completion_pct": 82.7, "is_delayed": True, "delay_reason": "Quality inspection backlog"},
    # Agriculture
    {"name": "YSR Rythu Bharosa", "scheme_type": "agriculture", "district": "West Godavari", "total_beneficiaries": 178000, "active_beneficiaries": 172000, "pending_applications": 980, "avg_pending_days": 14, "sla_days": 21, "disbursed_crores": 720, "target_crores": 750, "completion_pct": 96.0, "is_delayed": False},
    {"name": "YSR Rythu Bharosa", "scheme_type": "agriculture", "district": "Krishna", "total_beneficiaries": 145000, "active_beneficiaries": 139000, "pending_applications": 1120, "avg_pending_days": 16, "sla_days": 21, "disbursed_crores": 580, "target_crores": 610, "completion_pct": 95.1, "is_delayed": False},
    # Health
    {"name": "YSR Aarogyasri", "scheme_type": "health", "district": "Visakhapatnam", "total_beneficiaries": 320000, "active_beneficiaries": 310000, "pending_applications": 5600, "avg_pending_days": 8, "sla_days": 7, "disbursed_crores": 1200, "target_crores": 1400, "completion_pct": 85.7, "is_delayed": True, "delay_reason": "Hospital capacity constraints"},
    {"name": "YSR Aarogyasri", "scheme_type": "health", "district": "Nellore", "total_beneficiaries": 198000, "active_beneficiaries": 192000, "pending_applications": 2100, "avg_pending_days": 11, "sla_days": 7, "disbursed_crores": 780, "target_crores": 850, "completion_pct": 91.8, "is_delayed": True, "delay_reason": "Specialist referral backlog"},
]

AP_KPI_TEMPLATES = [
    {"metric_name": "Budget Utilization", "metric_category": "spending", "unit": "%", "target_value": 90.0},
    {"metric_name": "Avg File Clearance Days", "metric_category": "delivery", "unit": "days", "target_value": 20.0},
    {"metric_name": "Beneficiary Satisfaction", "metric_category": "satisfaction", "unit": "%", "target_value": 85.0},
    {"metric_name": "Compliance Score", "metric_category": "compliance", "unit": "%", "target_value": 95.0},
]

async def seed_data(db: AsyncSession):
    """Seed database with AP government mock data if empty."""
    count = (await db.execute(select(func.count(Department.id)))).scalar()
    if count and count > 0:
        return  # Already seeded

    try:
        # Create departments
        dept_map = {}
        for dept_data in AP_DEPARTMENTS:
            dept = Department(**dept_data)
            db.add(dept)
            await db.flush()
            dept_map[dept_data["code"]] = dept.id

        # Seed KPI metrics for each department
        for dept_data in AP_DEPARTMENTS:
            dept_id = dept_map[dept_data["code"]]
            utilization = dept_data["spent_crores"] / dept_data["budget_crores"] * 100
            clearance_days = dept_data["avg_file_clearance_days"]
            kpi_values = {
                "Budget Utilization": round(utilization, 1),
                "Avg File Clearance Days": float(clearance_days),
                "Beneficiary Satisfaction": round(max(60.0, 100.0 - clearance_days * 0.5), 1),
                "Compliance Score": round(min(98.0, 70.0 + utilization * 0.3), 1),
            }
            for tmpl in AP_KPI_TEMPLATES:
                current = kpi_values[tmpl["metric_name"]]
                is_anomalous = (
                    (tmpl["metric_name"] == "Budget Utilization" and current > 98.0) or
                    (tmpl["metric_name"] == "Avg File Clearance Days" and current > 45.0) or
                    (tmpl["metric_name"] == "Compliance Score" and current < 75.0)
                )
                trend = "improving" if current >= tmpl["target_value"] else "declining"
                kpi = KpiMetric(
                    department_id=dept_id,
                    metric_name=tmpl["metric_name"],
                    metric_category=tmpl["metric_category"],
                    current_value=current,
                    target_value=tmpl["target_value"],
                    unit=tmpl["unit"],
                    is_anomalous=is_anomalous,
                    trend=trend,
                )
                db.add(kpi)

        # Map scheme types to departments
        scheme_dept_map = {
            "pension": "SWTW",
            "housing": "MAUD",
            "agriculture": "AGR",
            "health": "HMFW",
            "education": "EDU",
        }

        for scheme_data in AP_SCHEMES:
            dept_code = scheme_dept_map.get(scheme_data["scheme_type"], "FIN")
            dept_id = dept_map[dept_code]
            scheme = Scheme(**scheme_data, department_id=dept_id)
            db.add(scheme)

        await db.commit()
    except IntegrityError:
        await db.rollback()
        return  # Another concurrent request already seeded
