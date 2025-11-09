#!/usr/bin/env python3
"""
Health check script for container orchestration
Returns 0 if healthy, 1 if unhealthy
"""

import sys
import requests
from datetime import datetime

def check_health():
    """Check if the application is healthy"""
    try:
        # Check dashboard API
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if bot status is available
            if 'bot_status' in data:
                print(f"✓ Health check passed - Status: {data['bot_status']}")
                return 0
            else:
                print("✗ Health check failed - Invalid response format")
                return 1
        else:
            print(f"✗ Health check failed - HTTP {response.status_code}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("✗ Health check failed - Cannot connect to dashboard")
        return 1
    except requests.exceptions.Timeout:
        print("✗ Health check failed - Request timeout")
        return 1
    except Exception as e:
        print(f"✗ Health check failed - {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(check_health())
