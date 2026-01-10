"""
Test suite for Reports API endpoints
Tests: GET /api/reports, GET /api/reports/export/{type}
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Get session token from environment or create one
SESSION_TOKEN = os.environ.get('TEST_SESSION_TOKEN', '')

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session with auth"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SESSION_TOKEN}"
    })
    return session


class TestReportsEndpoint:
    """Tests for GET /api/reports endpoint"""
    
    def test_reports_returns_200(self, api_client):
        """Test that reports endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/reports")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_reports_returns_all_required_fields(self, api_client):
        """Test that reports returns all 6 required aggregation fields"""
        response = api_client.get(f"{BASE_URL}/api/reports")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "pipeline_por_etapa",
            "leads_por_fuente", 
            "leads_por_sector",
            "servicios_demandados",
            "leads_por_propietario",
            "motivos_perdida"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_reports_pipeline_por_etapa_structure(self, api_client):
        """Test pipeline_por_etapa has correct structure with cantidad and valor"""
        response = api_client.get(f"{BASE_URL}/api/reports")
        data = response.json()
        
        pipeline = data.get("pipeline_por_etapa", {})
        expected_stages = ["nuevo", "contactado", "calificado", "propuesta", "negociacion", "ganado", "perdido"]
        
        for stage in expected_stages:
            assert stage in pipeline, f"Missing stage: {stage}"
            assert "cantidad" in pipeline[stage], f"Stage {stage} missing 'cantidad'"
            assert "valor" in pipeline[stage], f"Stage {stage} missing 'valor'"
    
    def test_reports_with_date_filter(self, api_client):
        """Test reports endpoint with date filter parameters"""
        response = api_client.get(
            f"{BASE_URL}/api/reports",
            params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-12-31"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
    
    def test_reports_total_leads_count(self, api_client):
        """Test that total_leads is returned"""
        response = api_client.get(f"{BASE_URL}/api/reports")
        data = response.json()
        assert "total_leads" in data
        assert isinstance(data["total_leads"], int)


class TestReportsExportEndpoints:
    """Tests for GET /api/reports/export/{type} endpoints"""
    
    def test_export_pipeline_csv(self, api_client):
        """Test export pipeline returns CSV"""
        response = api_client.get(f"{BASE_URL}/api/reports/export/pipeline")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "Etapa,Cantidad,Valor EUR" in response.text
    
    def test_export_fuentes_csv(self, api_client):
        """Test export fuentes returns CSV"""
        response = api_client.get(f"{BASE_URL}/api/reports/export/fuentes")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "Fuente,Cantidad" in response.text
    
    def test_export_sectores_csv(self, api_client):
        """Test export sectores returns CSV"""
        response = api_client.get(f"{BASE_URL}/api/reports/export/sectores")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "Sector,Cantidad" in response.text
    
    def test_export_servicios_csv(self, api_client):
        """Test export servicios returns CSV"""
        response = api_client.get(f"{BASE_URL}/api/reports/export/servicios")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "Servicio,Leads Interesados" in response.text
    
    def test_export_propietarios_csv(self, api_client):
        """Test export propietarios returns CSV"""
        response = api_client.get(f"{BASE_URL}/api/reports/export/propietarios")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "Propietario,Cantidad Leads,Valor EUR" in response.text
    
    def test_export_perdidas_csv(self, api_client):
        """Test export perdidas returns CSV"""
        response = api_client.get(f"{BASE_URL}/api/reports/export/perdidas")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "Motivo,Cantidad" in response.text
    
    def test_export_invalid_type_returns_400(self, api_client):
        """Test that invalid export type returns 400"""
        response = api_client.get(f"{BASE_URL}/api/reports/export/invalid_type")
        assert response.status_code == 400
    
    def test_export_with_date_filter(self, api_client):
        """Test export with date filter parameters"""
        response = api_client.get(
            f"{BASE_URL}/api/reports/export/pipeline",
            params={"fecha_inicio": "2025-01-01", "fecha_fin": "2025-12-31"}
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


class TestReportsAuth:
    """Tests for reports authentication"""
    
    def test_reports_requires_auth(self):
        """Test that reports endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/reports")
        assert response.status_code == 401
    
    def test_export_requires_auth(self):
        """Test that export endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/reports/export/pipeline")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
