import json
from app.services.win_client import WinClient
from app.services.log_collector import LogCollector

# Mock class to simulate Windows Shell output
class MockWinClient(WinClient):
    def run_ps(self, cmd):
        # Return a sample JSON output that mimics the real PowerShell script result
        mock_data = [
            {
                "Timestamp": "2023-10-27 10:00:00",
                "IpAddress": "192.168.1.50",
                "TargetUserName": "hacker",
                "EventId": 4625
            },
            {
                "Timestamp": "2023-10-27 10:05:00",
                "IpAddress": "-",
                "TargetUserName": "admin",
                "EventId": 4625
            }
        ]
        return json.dumps(mock_data)

def test_mock_parsing():
    print("Testowanie parsowania logów Windows (Mock)...")
    
    with MockWinClient() as client:
        logs = LogCollector.get_windows_logs(client)
        
    print(f"Pobrano {len(logs)} logów.")
    
    assert len(logs) == 2
    assert logs[0]['source_ip'] == "192.168.1.50"
    assert logs[0]['user'] == "hacker"
    assert logs[0]['alert_type'] == "WIN_FAILED_LOGIN"
    
    assert logs[1]['source_ip'] == "LOCAL_CONSOLE"
    assert logs[1]['user'] == "admin"
    
    print("✅ Parsowanie działa poprawnie.")

if __name__ == "__main__":
    test_mock_parsing()
