#!/usr/bin/env python
"""
Auto-Tuning Switcher - Automatically switches TCP auto-tuning based on network activity
(You'll need to go into the code and change the .exe files to ignore)
"""

import psutil
import time
import subprocess
import sys
import ctypes
import argparse
import logging
from collections import defaultdict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autotuning_switcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'download_threshold_mbps': 2.0,  # 2 Mbps
    'detection_seconds': 10,          # Time to confirm download
    'cooldown_seconds': 30,           # Wait before switching back
    'check_interval': 2,               # Seconds between checks
    'gaming_processes': [
        'cs2.exe',
        'valorant.exe'
    ],
    'ignored_processes': [
        'System',
        'svchost.exe',
        'Idle'
    ]
}

class AutotuningSwitcher:
    def __init__(self, config=CONFIG):
        self.config = config
        self.download_active = False
        self.high_traffic_start = None
        self.previous_data = {}
        self.current_state = self.get_current_autotuning()
        
        logger.info(f"Auto-Tuning Switcher initialized")
        logger.info(f"Current auto-tuning state: {self.current_state}")
        
        if not self.is_admin():
            logger.error("Administrator privileges required!")
            sys.exit(1)
    
    def is_admin(self):
        """Check for admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def get_current_autotuning(self):
        """Get current auto-tuning setting"""
        try:
            result = subprocess.run(
                "netsh int tcp show global", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'Receive Window Auto-Tuning Level' in line:
                    return line.split(':')[-1].strip().lower()
        except Exception as e:
            logger.error(f"Failed to get auto-tuning state: {e}")
        return None
    
    def set_autotuning(self, mode):
        """Change auto-tuning level"""
        if mode not in ['normal', 'disabled', 'highlyrestricted', 'restricted', 'experimental']:
            logger.error(f"Invalid mode: {mode}")
            return False
        
        try:
            cmd = f"netsh int tcp set global autotuninglevel={mode}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.current_state = mode
                logger.info(f"Auto-tuning set to: {mode}")
                return True
            else:
                logger.error(f"Failed to set auto-tuning: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error setting auto-tuning: {e}")
            return False
    
    def get_process_network_usage(self):
        """Get approximate network usage per process"""
        current = {}
        
        try:
            # Get all connections
            connections = psutil.net_connections()
            
            # Group by PID
            pid_connections = defaultdict(list)
            for conn in connections:
                if conn.pid and conn.pid > 0:
                    pid_connections[conn.pid].append(conn)
            
            # Get I/O for processes with connections
            for pid, conns in pid_connections.items():
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                    
                    # Skip ignored processes
                    if proc_name.lower() in [p.lower() for p in self.config['ignored_processes']]:
                        continue
                    
                    io_counters = proc.io_counters()
                    if io_counters:
                        current[pid] = {
                            'name': proc_name,
                            'bytes_recv': io_counters.read_bytes,
                            'bytes_sent': io_counters.write_bytes,
                            'connections': len(conns)
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting process network usage: {e}")
        
        return current
    
    def is_gaming_process(self, process_name):
        """Check if process is a known game"""
        return process_name.lower() in [p.lower() for p in self.config['gaming_processes']]
    
    def monitor(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop...")
        logger.info(f"Threshold: {self.config['download_threshold_mbps']} Mbps for {self.config['detection_seconds']}s")
        
        self.previous_data = self.get_process_network_usage()
        
        try:
            while True:
                time.sleep(self.config['check_interval'])
                current_data = self.get_process_network_usage()
                
                total_download_bps = 0
                active_games = []
                
                # Calculate speeds
                for pid, current in current_data.items():
                    if pid in self.previous_data:
                        prev = self.previous_data[pid]
                        
                        download_bps = (current['bytes_recv'] - prev['bytes_recv']) / self.config['check_interval']
                        upload_bps = (current['bytes_sent'] - prev['bytes_sent']) / self.config['check_interval']
                        download_mbps = download_bps * 8 / 1_000_000
                        
                        # Track total download
                        total_download_bps += download_bps
                        
                        # Check for active games
                        if self.is_gaming_process(current['name']) and (download_mbps > 0.1 or upload_bps > 0):
                            active_games.append(current['name'])
                        
                        # Log high-bandwidth processes
                        if download_mbps > 1.0:  # Log processes using > 1 Mbps
                            logger.debug(f"Process {current['name']}: {download_mbps:.2f} Mbps down")
                
                total_download_mbps = total_download_bps * 8 / 1_000_000
                
                # Detection logic
                if total_download_mbps > self.config['download_threshold_mbps']:
                    if self.high_traffic_start is None:
                        self.high_traffic_start = time.time()
                        logger.info(f"High traffic detected: {total_download_mbps:.2f} Mbps")
                    elif time.time() - self.high_traffic_start > self.config['detection_seconds']:
                        if not self.download_active:
                            logger.info(f"Large download confirmed: {total_download_mbps:.2f} Mbps")
                            if active_games:
                                logger.info(f"Active games detected: {active_games} - not switching")
                            else:
                                self.set_autotuning("normal")
                                self.download_active = True
                else:
                    if self.download_active:
                        logger.info(f"Traffic dropped to {total_download_mbps:.2f} Mbps, starting cooldown")
                        time.sleep(self.config['cooldown_seconds'])
                        
                        # Verify traffic is still low
                        verify_data = self.get_process_network_usage()
                        verify_total = 0
                        for pid, current in verify_data.items():
                            if pid in current_data:
                                verify_total += current['bytes_recv']
                        
                        if verify_total < self.config['download_threshold_mbps'] * 125000:  # Approx conversion
                            self.set_autotuning("disabled")
                            self.download_active = False
                            logger.info("Returned to gaming mode")
                    
                    self.high_traffic_start = None
                
                self.previous_data = current_data
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            # Restore gaming mode on exit
            if self.download_active:
                self.set_autotuning("disabled")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Auto-Tuning Switcher')
    parser.add_argument('--threshold', type=float, default=2.0,
                       help='Download threshold in Mbps (default: 2.0)')
    parser.add_argument('--detect-time', type=int, default=10,
                       help='Seconds to confirm download (default: 10)')
    parser.add_argument('--cooldown', type=int, default=30,
                       help='Cooldown seconds before switching back (default: 30)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Update config with command line args
    CONFIG['download_threshold_mbps'] = args.threshold
    CONFIG['detection_seconds'] = args.detect_time
    CONFIG['cooldown_seconds'] = args.cooldown
    
    switcher = AutotuningSwitcher(CONFIG)
    switcher.monitor()

if __name__ == "__main__":
    main()