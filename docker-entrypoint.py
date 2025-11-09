#!/usr/bin/env python3
"""
Entrypoint script for Docker deployment
Handles both bot and dashboard startup based on environment
"""

import os
import sys
import subprocess
import signal
from multiprocessing import Process

def run_bot():
    """Run the trading bot"""
    print("Starting Trading Bot...")
    subprocess.run([sys.executable, "main.py"])

def run_dashboard():
    """Run the dashboard"""
    print("Starting Dashboard...")
    host = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    port = os.getenv('DASHBOARD_PORT', '5000')
    subprocess.run([sys.executable, "run_dashboard.py", "--host", host, "--port", port])

def run_all():
    """Run both bot and dashboard"""
    print("Starting Trading Bot + Dashboard...")
    
    # Start processes
    dashboard_process = Process(target=run_dashboard)
    bot_process = Process(target=run_bot)
    
    dashboard_process.start()
    print(f"Dashboard started (PID: {dashboard_process.pid})")
    
    # Give dashboard time to start
    import time
    time.sleep(3)
    
    bot_process.start()
    print(f"Bot started (PID: {bot_process.pid})")
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\nShutting down services...")
        bot_process.terminate()
        dashboard_process.terminate()
        bot_process.join(timeout=5)
        dashboard_process.join(timeout=5)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for processes
    try:
        bot_process.join()
        dashboard_process.join()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    mode = os.getenv('RUN_MODE', 'all')
    
    if mode == 'bot':
        run_bot()
    elif mode == 'dashboard':
        run_dashboard()
    else:
        run_all()
