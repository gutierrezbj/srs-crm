#!/usr/bin/env python3
"""
Backend API Testing for System Rapid Solutions CRM
Tests all API endpoints with authentication
"""

import requests
import sys
import json
from datetime import datetime
import io
import csv

class CRMAPITester:
    def __init__(self, base_url="https://dronesys-crm.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = "test_session_1768065365846"  # Updated session token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.session_token}'
        }
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_lead_id = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_root_endpoint(self):
        """Test GET /api/ - API info"""
        try:
            response = requests.get(f"{self.api_url}/")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'N/A')}"
            self.log_test("GET /api/ - API Info", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/ - API Info", False, str(e))
            return False

    def test_auth_me(self):
        """Test GET /api/auth/me - Get current user"""
        try:
            response = requests.get(f"{self.api_url}/auth/me", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", User: {data.get('name', 'N/A')}, Role: {data.get('role', 'N/A')}"
            self.log_test("GET /api/auth/me - Current User", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/auth/me - Current User", False, str(e))
            return False

    def test_create_lead(self):
        """Test POST /api/leads - Create lead"""
        lead_data = {
            "empresa": "Test Company API",
            "contacto": "John Doe",
            "email": "john.doe@testcompany.com",
            "telefono": "+34 600 123 456",
            "cargo": "CTO",
            "sector": "Tecnología",
            "valor_estimado": 15000.0,
            "etapa": "nuevo",
            "notas": "Lead creado desde test automatizado"
        }
        
        try:
            response = requests.post(f"{self.api_url}/leads", json=lead_data, headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                self.created_lead_id = data.get('lead_id')
                details += f", Lead ID: {self.created_lead_id}"
            self.log_test("POST /api/leads - Create Lead", success, details)
            return success
        except Exception as e:
            self.log_test("POST /api/leads - Create Lead", False, str(e))
            return False

    def test_get_leads(self):
        """Test GET /api/leads - Get leads list"""
        try:
            response = requests.get(f"{self.api_url}/leads", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Count: {len(data)} leads"
            self.log_test("GET /api/leads - Get Leads List", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/leads - Get Leads List", False, str(e))
            return False

    def test_get_lead_by_id(self):
        """Test GET /api/leads/{id} - Get single lead"""
        if not self.created_lead_id:
            self.log_test("GET /api/leads/{id} - Get Single Lead", False, "No lead ID available")
            return False
            
        try:
            response = requests.get(f"{self.api_url}/leads/{self.created_lead_id}", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Company: {data.get('empresa', 'N/A')}"
            self.log_test("GET /api/leads/{id} - Get Single Lead", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/leads/{id} - Get Single Lead", False, str(e))
            return False

    def test_update_lead(self):
        """Test PUT /api/leads/{id} - Update lead"""
        if not self.created_lead_id:
            self.log_test("PUT /api/leads/{id} - Update Lead", False, "No lead ID available")
            return False
            
        update_data = {
            "empresa": "Test Company API Updated",
            "valor_estimado": 20000.0,
            "etapa": "contactado"
        }
        
        try:
            response = requests.put(f"{self.api_url}/leads/{self.created_lead_id}", json=update_data, headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Updated Company: {data.get('empresa', 'N/A')}"
            self.log_test("PUT /api/leads/{id} - Update Lead", success, details)
            return success
        except Exception as e:
            self.log_test("PUT /api/leads/{id} - Update Lead", False, str(e))
            return False

    def test_update_lead_stage(self):
        """Test PATCH /api/leads/{id}/stage - Change lead stage"""
        if not self.created_lead_id:
            self.log_test("PATCH /api/leads/{id}/stage - Change Stage", False, "No lead ID available")
            return False
            
        try:
            response = requests.patch(f"{self.api_url}/leads/{self.created_lead_id}/stage?etapa=calificado", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", New Stage: {data.get('etapa', 'N/A')}"
            self.log_test("PATCH /api/leads/{id}/stage - Change Stage", success, details)
            return success
        except Exception as e:
            self.log_test("PATCH /api/leads/{id}/stage - Change Stage", False, str(e))
            return False

    def test_get_leads_stats(self):
        """Test GET /api/leads/stats - Dashboard stats"""
        try:
            response = requests.get(f"{self.api_url}/leads/stats", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Total Leads: {data.get('total_leads', 0)}, Pipeline: €{data.get('total_pipeline', 0)}"
            self.log_test("GET /api/leads/stats - Dashboard Stats", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/leads/stats - Dashboard Stats", False, str(e))
            return False

    def test_create_activity(self):
        """Test POST /api/leads/{id}/activities - Create activity"""
        if not self.created_lead_id:
            self.log_test("POST /api/leads/{id}/activities - Create Activity", False, "No lead ID available")
            return False
            
        activity_data = {
            "tipo": "nota",
            "descripcion": "Actividad de prueba desde test automatizado"
        }
        
        try:
            response = requests.post(f"{self.api_url}/leads/{self.created_lead_id}/activities", json=activity_data, headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Activity ID: {data.get('activity_id', 'N/A')}"
            self.log_test("POST /api/leads/{id}/activities - Create Activity", success, details)
            return success
        except Exception as e:
            self.log_test("POST /api/leads/{id}/activities - Create Activity", False, str(e))
            return False

    def test_get_activities(self):
        """Test GET /api/leads/{id}/activities - Get activities"""
        if not self.created_lead_id:
            self.log_test("GET /api/leads/{id}/activities - Get Activities", False, "No lead ID available")
            return False
            
        try:
            response = requests.get(f"{self.api_url}/leads/{self.created_lead_id}/activities", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Activities Count: {len(data)}"
            self.log_test("GET /api/leads/{id}/activities - Get Activities", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/leads/{id}/activities - Get Activities", False, str(e))
            return False

    def test_export_leads(self):
        """Test GET /api/leads/export - Export CSV"""
        try:
            response = requests.get(f"{self.api_url}/leads/export", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                # Check if it's valid CSV
                content = response.text
                csv_reader = csv.reader(io.StringIO(content))
                rows = list(csv_reader)
                details += f", CSV Rows: {len(rows)}"
            self.log_test("GET /api/leads/export - Export CSV", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/leads/export - Export CSV", False, str(e))
            return False

    def test_import_leads(self):
        """Test POST /api/leads/import - Import CSV"""
        # Create test CSV content
        csv_content = """empresa,contacto,email,telefono,cargo,sector,valor_estimado,etapa,notas
Test Import Company,Jane Smith,jane@import.com,+34 600 987 654,Manager,Servicios,8000,nuevo,Importado desde test
"""
        
        try:
            files = {'file': ('test_import.csv', csv_content, 'text/csv')}
            # Remove Content-Type header for multipart upload
            headers = {'Authorization': f'Bearer {self.session_token}'}
            response = requests.post(f"{self.api_url}/leads/import", files=files, headers=headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Imported: {data.get('imported', 0)} leads"
            self.log_test("POST /api/leads/import - Import CSV", success, details)
            return success
        except Exception as e:
            self.log_test("POST /api/leads/import - Import CSV", False, str(e))
            return False

    def test_enrich_lead(self):
        """Test POST /api/leads/enrich - Apollo API endpoint"""
        enrich_data = {
            "email": "john.doe@testcompany.com",
            "empresa": "Test Company Enriched",
            "telefono": "+34 600 111 222"
        }
        
        try:
            # Remove Authorization header as this is external API endpoint
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{self.api_url}/leads/enrich", json=enrich_data, headers=headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Updated Fields: {data.get('updated_fields', [])}"
            self.log_test("POST /api/leads/enrich - Apollo API", success, details)
            return success
        except Exception as e:
            self.log_test("POST /api/leads/enrich - Apollo API", False, str(e))
            return False

    def test_get_sectors(self):
        """Test GET /api/sectors - Get unique sectors"""
        try:
            response = requests.get(f"{self.api_url}/sectors", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Sectors Count: {len(data)}"
            self.log_test("GET /api/sectors - Get Sectors", success, details)
            return success
        except Exception as e:
            self.log_test("GET /api/sectors - Get Sectors", False, str(e))
            return False

    def test_delete_lead(self):
        """Test DELETE /api/leads/{id} - Delete lead (run last)"""
        if not self.created_lead_id:
            self.log_test("DELETE /api/leads/{id} - Delete Lead", False, "No lead ID available")
            return False
            
        try:
            response = requests.delete(f"{self.api_url}/leads/{self.created_lead_id}", headers=self.headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'N/A')}"
            self.log_test("DELETE /api/leads/{id} - Delete Lead", success, details)
            return success
        except Exception as e:
            self.log_test("DELETE /api/leads/{id} - Delete Lead", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print(f"🚀 Starting CRM API Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Session Token: {self.session_token[:20]}...")
        print("-" * 60)

        # Test sequence - order matters for dependencies
        test_methods = [
            self.test_root_endpoint,
            self.test_auth_me,
            self.test_create_lead,
            self.test_get_leads,
            self.test_get_lead_by_id,
            self.test_update_lead,
            self.test_update_lead_stage,
            self.test_get_leads_stats,
            self.test_create_activity,
            self.test_get_activities,
            self.test_export_leads,
            self.test_import_leads,
            self.test_enrich_lead,
            self.test_get_sectors,
            self.test_delete_lead  # Run last to clean up
        ]

        for test_method in test_methods:
            test_method()

        print("-" * 60)
        print(f"📊 Tests completed: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

    def get_failed_tests(self):
        """Get list of failed tests"""
        return [test for test in self.test_results if not test['success']]

def main():
    tester = CRMAPITester()
    exit_code = tester.run_all_tests()
    
    # Print failed tests summary
    failed_tests = tester.get_failed_tests()
    if failed_tests:
        print("\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"  - {test['test']}: {test['details']}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())