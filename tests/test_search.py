import os
import pytest
from uuid import UUID
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add the parent directory to the Python path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Load environment variables
load_dotenv()
TEST_USER_ID = os.getenv("TEST_USER_ID")

client = TestClient(app)

def test_search_memories():
    params = {
        "user_id": TEST_USER_ID,
        "query": "political",
        "limit": 5,
        "include_details": True
    }
    
    response = client.get("/memories/search", params=params)
    assert response.status_code == 200
    results = response.json()
    
    assert isinstance(results, list)
    assert len(results) <= params["limit"]
    
    for result in results:
        assert isinstance(result, dict)
        assert all(key in result for key in ["id", "created_at", "structured", "status"])
        
        # Validate UUID format
        try:
            UUID(str(result["id"]))  # Convert to string first
        except ValueError:
            pytest.fail(f"Invalid UUID format: {result['id']}")
            
        assert isinstance(result["structured"], dict)
        assert "title" in result["structured"]
        assert "overview" in result["structured"]

def test_search_memories_invalid_user():
    params = {
        "user_id": "nonexistent-user-123",
        "query": "political",
        "limit": 5
    }
    response = client.get("/memories/search", params=params)
    # If your API returns empty results instead of 404, update this test
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_search_memories_no_results():
    params = {
        "user_id": TEST_USER_ID,
        "query": "xyznonexistentquery123",
        "limit": 5
    }
    response = client.get("/memories/search", params=params)
    assert response.status_code == 200
    results = response.json()
    
    # Option 1: Check if results are less relevant
    if results:
        # Print results for debugging
        print("\nSearch results for nonsense query:")
        for result in results:
            print(f"Title: {result['structured'].get('title')}")
            print(f"Category: {result['structured'].get('category')}")
            print("---")
            
        # Test that political content isn't ranked first
        first_result = results[0]
        assert (
            "politic" not in first_result["structured"].get("title", "").lower() and
            first_result["structured"].get("category", "").lower() != "politics"
        ), "Political content shouldn't be most relevant for nonsense query"
        
        # Option 2: Add relevance score to API response and test that
        # if "relevance_score" in results[0]:
        #     assert results[0]["relevance_score"] < 0.5, "Relevance should be low for nonsense query"

def test_search_memories_pagination():
    for limit in [1, 3, 5]:
        params = {
            "user_id": TEST_USER_ID,
            "query": "political",
            "limit": limit
        }
        response = client.get("/memories/search", params=params)
        assert response.status_code == 200
        results = response.json()
        assert len(results) <= limit

@pytest.mark.parametrize("include_details", [True, False])
def test_search_memories_detail_levels(include_details):
    params = {
        "user_id": TEST_USER_ID,
        "query": "political",
        "limit": 1,
        "include_details": include_details
    }
    response = client.get("/memories/search", params=params)
    assert response.status_code == 200
    results = response.json()
    
    if results:
        result = results[0]
        if include_details:
            # Update based on what fields are actually included when include_details=True
            assert isinstance(result["structured"], dict)
            assert "title" in result["structured"]
            assert "overview" in result["structured"]
            # Only assert transcript_segments if your API actually returns them
            # assert "transcript_segments" in result
        else:
            assert "transcript_segments" not in result
            assert "plugins_results" not in result
            assert "external_data" not in result

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup code if needed
    yield
    # Teardown code if needed

def test_search_relevance():
    """Test that search results are properly ranked by relevance"""
    political_params = {
        "user_id": TEST_USER_ID,
        "query": "political elections democracy",
        "limit": 5
    }
    
    finance_params = {
        "user_id": TEST_USER_ID,
        "query": "finance banking money",
        "limit": 5
    }
    
    # Test political query
    political_response = client.get("/memories/search", params=political_params)
    political_results = political_response.json()
    
    if political_results:
        first_result = political_results[0]
        assert (
            "politic" in first_result["structured"].get("title", "").lower() or
            first_result["structured"].get("category", "").lower() == "politics"
        ), "Political content should be ranked first for political query"
    
    # Test finance query
    finance_response = client.get("/memories/search", params=finance_params)
    finance_results = finance_response.json()
    
    if finance_results:
        first_result = finance_results[0]
        assert (
            "finance" in first_result["structured"].get("category", "").lower() or
            any(
                term in first_result["structured"].get("title", "").lower() 
                for term in ["finance", "money", "payment", "banking"]
            )
        ), "Financial content should be ranked first for finance query"