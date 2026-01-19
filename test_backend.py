"""
Comprehensive Backend API Test Suite
Tests all endpoints and provides detailed results
"""
import requests
import sys
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://localhost:6050/api"
TIMEOUT = 5  # seconds

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_result(self, endpoint, status, details=""):
        self.tests.append({
            "endpoint": endpoint,
            "status": status,
            "details": details
        })
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "="*60)
        print(f"{Fore.CYAN}TEST SUMMARY")
        print("="*60)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Fore.GREEN}✓ Passed: {self.passed}/{total}")
        print(f"{Fore.RED}✗ Failed: {self.failed}/{total}")
        print(f"{Fore.YELLOW}Pass Rate: {pass_rate:.1f}%")
        print("="*60 + "\n")
        
        if self.failed == 0:
            print(f"{Fore.GREEN}🎉 ALL TESTS PASSED! Backend is fully operational!")
        else:
            print(f"{Fore.RED}⚠️  Some tests failed. Check details above.")

results = TestResults()

def test_endpoint(name, url, method="GET", expected_fields=None):
    """Test a single endpoint"""
    print(f"\n{Fore.YELLOW}Testing: {name}")
    print(f"  URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        else:
            response = requests.post(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check expected fields if provided
            if expected_fields:
                if isinstance(data, list):
                    if len(data) > 0:
                        missing = [f for f in expected_fields if f not in data[0]]
                    else:
                        missing = []
                else:
                    missing = [f for f in expected_fields if f not in data]
                
                if missing:
                    print(f"  {Fore.RED}✗ FAIL - Missing fields: {missing}")
                    results.add_result(name, "FAIL", f"Missing fields: {missing}")
                    return False
            
            # Success
            if isinstance(data, list):
                print(f"  {Fore.GREEN}✓ PASS - Returned {len(data)} items")
                results.add_result(name, "PASS", f"{len(data)} items")
            else:
                print(f"  {Fore.GREEN}✓ PASS - Response OK")
                results.add_result(name, "PASS", "Response OK")
            return True
        else:
            print(f"  {Fore.RED}✗ FAIL - Status {response.status_code}")
            results.add_result(name, "FAIL", f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  {Fore.RED}✗ FAIL - Cannot connect to server")
        results.add_result(name, "FAIL", "Connection refused")
        return False
    except requests.exceptions.Timeout:
        print(f"  {Fore.RED}✗ FAIL - Request timeout")
        results.add_result(name, "FAIL", "Timeout")
        return False
    except Exception as e:
        print(f"  {Fore.RED}✗ FAIL - {str(e)}")
        results.add_result(name, "FAIL", str(e))
        return False

def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║   PEAK HOUR DISPATCH AI - BACKEND API TEST SUITE       ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}\n")
    
    # Test 1: Drivers API
    print(f"\n{Fore.CYAN}═══ DRIVER ENDPOINTS ═══")
    test_endpoint(
        "GET /drivers - List all drivers",
        f"{BASE_URL}/drivers",
        expected_fields=["driver_id", "name", "online_status"]
    )
    
    test_endpoint(
        "GET /drivers/online/locations - Online driver locations",
        f"{BASE_URL}/drivers/online/locations",
        expected_fields=["driver_id", "latitude", "longitude"]
    )
    
    # Test 2: Rides API
    print(f"\n{Fore.CYAN}═══ RIDE ENDPOINTS ═══")
    test_endpoint(
        "GET /rides - List all rides",
        f"{BASE_URL}/rides",
        expected_fields=["ride_id", "status"]
    )
    
    # Test 3: Metrics API
    print(f"\n{Fore.CYAN}═══ METRICS ENDPOINTS ═══")
    test_endpoint(
        "GET /metrics/system - System KPIs",
        f"{BASE_URL}/metrics/system",
        expected_fields=["total_rides", "total_drivers", "online_drivers"]
    )
    
    test_endpoint(
        "GET /metrics/performance - Performance analytics",
        f"{BASE_URL}/metrics/performance",
        expected_fields=["overall_acceptance_rate", "total_trip_outcomes"]
    )
    
    # Test 4: Demand/Heatmap API
    print(f"\n{Fore.CYAN}═══ DEMAND FORECASTING ENDPOINTS ═══")
    test_endpoint(
        "GET /demand/zones - Geographic zones",
        f"{BASE_URL}/demand/zones",
        expected_fields=["zone_id", "center_lat", "center_lng"]
    )
    
    test_endpoint(
        "GET /demand/heatmap - Demand heatmap data",
        f"{BASE_URL}/demand/heatmap",
        expected_fields=["zone_id", "demand_score"]
    )
    
    test_endpoint(
        "GET /demand/hotspots - Top hotspots",
        f"{BASE_URL}/demand/hotspots?top_n=3"
    )
    
    # Print summary
    results.print_summary()
    
    # Return exit code
    return 0 if results.failed == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user")
        sys.exit(1)
