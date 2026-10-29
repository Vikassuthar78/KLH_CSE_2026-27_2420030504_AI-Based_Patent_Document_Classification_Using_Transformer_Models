"""
Tests for API endpoints
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


@pytest.fixture
def sync_client():
    """Create a synchronous test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as client:
        yield client


class TestHealthEndpoints:
    """Test health and status endpoints."""

    def test_health(self, sync_client):
        """Test health endpoint returns 200."""
        response = sync_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_status(self, sync_client):
        """Test status endpoint returns app info."""
        response = sync_client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "version" in data


class TestDatasetEndpoints:
    """Test dataset API endpoints."""

    def test_discover_datasets(self, sync_client):
        """Test dataset discovery endpoint."""
        response = sync_client.get("/api/v1/datasets/discover")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_dataset_preview(self, sync_client):
        """Test dataset preview endpoint."""
        response = sync_client.get("/api/v1/datasets/preview?page=1&page_size=10")
        assert response.status_code in [200, 404]  # 404 if no dataset configured

    def test_dataset_stats(self, sync_client):
        """Test dataset stats endpoint."""
        response = sync_client.get("/api/v1/datasets/stats")
        assert response.status_code in [200, 404]


class TestExperimentEndpoints:
    """Test experiment API endpoints."""

    def test_list_experiments(self, sync_client):
        """Test listing experiments."""
        response = sync_client.get("/api/v1/experiments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTaxonomyEndpoints:
    """Test taxonomy API endpoints."""

    def test_taxonomy_tree(self, sync_client):
        """Test taxonomy tree endpoint."""
        response = sync_client.get("/api/v1/taxonomy/tree")
        assert response.status_code in [200, 404]

    def test_taxonomy_search(self, sync_client):
        """Test taxonomy search endpoint."""
        response = sync_client.get("/api/v1/taxonomy/search?query=G06")
        assert response.status_code in [200, 404]

