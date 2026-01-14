
import datetime
import json
from app.services.log_collector import LogCollector
from app.services.win_client import WinClient

def test_fix():
    print("--- Verifying LogCollector.get_windows_logs fix ---")
    
    # Simulate a last fetch time
    last_fetch_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
    print(f"Testing with last_fetch_time: {last_fetch_time}")

    try:
        with WinClient() as client:
            # This call previously failed with TypeError: got an unexpected keyword argument 'last_fetch'
            # We are now testing if 'last_fetch_time' is accepted and works.
            logs = LogCollector.get_windows_logs(client, last_fetch_time=last_fetch_time)
            
            print(f"✅ Success! Call accepted. Retrieved {len(logs)} logs.")
            for log in logs:
                print(f"Log: {log['timestamp']} - {log['user']} - {log['source_ip']}")

    except TypeError as e:
        print(f"❌ FAILED with TypeError: {e}")
    except Exception as e:
        print(f"❌ FAILED with Exception: {e}")

if __name__ == "__main__":
    test_fix()
