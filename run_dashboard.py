#!/usr/bin/env python3
"""
Script to run the trading bot dashboard
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitoring.dashboard import run_dashboard

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Trading Bot Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Dashboard host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Dashboard port (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Starting Trading Bot Dashboard")
    print("=" * 60)
    print(f"Dashboard URL: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    run_dashboard(host=args.host, port=args.port, debug=args.debug)
