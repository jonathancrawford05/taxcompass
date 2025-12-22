"""
Quick API test script
Tests the analysis endpoints
"""
import requests
import json
from datetime import date, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def test_quick_analysis():
    """Test the quick-analysis endpoint"""

    # Sample user profile
    user_profile = {
        "citizenship": ["CA"],
        "current_country": "CA",
        "destination_country": "AE",
        "departure_date": (date.today() + timedelta(days=90)).isoformat(),
        "marital_status": "married",
        "has_spouse": True,
        "spouse_location": "CA",
        "has_dependents": True,
        "dependents_location": "CA",
        "owns_home_origin": True,
        "home_disposition": "rent",
        "owns_home_destination": False,
        "employment_type": "employee",
        "employer_country": "AE",
        "annual_income": "150000",
        "has_rental_property": False,
        "investment_accounts_balance": "50000",
        "rrsp_balance": "75000",
        "tfsa_balance": "25000",
        "unrealized_capital_gains": None,
        "ties_score": {}
    }

    # Create analysis request
    analysis_request = {
        "title": "Canada to UAE Move - Test",
        "origin_country": "CA",
        "destination_country": "AE",
        "departure_date": (date.today() + timedelta(days=90)).isoformat(),
        "user_profile": user_profile
    }

    print("=" * 80)
    print("Testing TaxCompass Analysis API")
    print("=" * 80)

    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Quick analysis
    print("\n2. Creating and running analysis...")
    print(f"Analyzing: {analysis_request['origin_country']} → {analysis_request['destination_country']}")

    response = requests.post(
        f"{BASE_URL}/api/v1/analysis/quick-analysis",
        json=analysis_request,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Analysis ID: {result.get('id')}")
        print(f"Status: {result.get('status')}")
        print(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
        print(f"\nOrigin Status ({result.get('origin_country')}): {result.get('origin_residency_status')}")
        print(f"Destination Status ({result.get('destination_country')}): {result.get('destination_residency_status')}")

        if result.get('recommendations'):
            print(f"\nRecommendations:")
            for i, rec in enumerate(result.get('recommendations', []), 1):
                print(f"  {i}. {rec}")

        if result.get('key_factors'):
            print(f"\nKey Factors:")
            for factor in result.get('key_factors', [])[:5]:  # First 5
                print(f"  - {factor}")

        if result.get('red_flags'):
            print(f"\nRed Flags:")
            for flag in result.get('red_flags', []):
                print(f"  ⚠️  {flag}")

        print(f"\nProcessing Time: {result.get('processing_time_seconds', 'N/A')}s")
        print("=" * 80)
    else:
        print(f"Error: {response.text}")

    # Test 3: List analyses
    print("\n3. Listing all analyses...")
    response = requests.get(f"{BASE_URL}/api/v1/analysis")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        analyses = response.json()
        print(f"Found {len(analyses)} analysis(es)")
        for analysis in analyses[:3]:  # Show first 3
            print(f"  - {analysis.get('title')} (Status: {analysis.get('status')})")

if __name__ == "__main__":
    try:
        test_quick_analysis()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API at http://localhost:8000")
        print("Make sure the backend container is running: docker-compose ps")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
