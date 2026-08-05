from app.health.health_service import HealthService


def test_health_status():
    service = HealthService()

    response = service.status()

    assert response["status"] == "healthy"
