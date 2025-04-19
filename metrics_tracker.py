from typing import Dict
from datetime import datetime
import json
import logging

class MetricsTracker:
    def __init__(self):
        self.metrics = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'bounces': 0,
            'spam_reports': 0,
            'delivery_times': [],
            'failures': {}
        }
    
    def track_delivery(self, recipient: str) -> None:
        """Track successful delivery."""
        self.metrics['total_sent'] += 1
        self.metrics['successful'] += 1
        self.metrics['delivery_times'].append(datetime.now().timestamp())
    
    def track_failure(self, recipient: str, error: str) -> None:
        """Track delivery failure."""
        self.metrics['total_sent'] += 1
        self.metrics['failed'] += 1
        
        if error not in self.metrics['failures']:
            self.metrics['failures'][error] = 0
        self.metrics['failures'][error] += 1
    
    def track_bounce(self, recipient: str, bounce_type: str) -> None:
        """Track email bounce."""
        self.metrics['bounces'] += 1
        logging.warning(f"Bounce recorded for {recipient}: {bounce_type}")
    
    def track_spam_report(self, recipient: str) -> None:
        """Track spam report."""
        self.metrics['spam_reports'] += 1
        logging.warning(f"Spam report from {recipient}")
    
    def get_metrics(self) -> Dict:
        """Get current metrics."""
        return self.metrics
    
    def save_metrics(self, filename: str) -> None:
        """Save metrics to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=4) 