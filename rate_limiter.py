from datetime import datetime, timedelta
import logging
from typing import Dict
import time

class RateLimiter:
    def __init__(
        self,
        max_per_second: int = 10,
        max_per_hour: int = 1000,
        max_per_day: int = 10000
    ):
        self.max_per_second = max_per_second
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        
        self.current_second = datetime.now()
        self.current_hour = self.current_second
        self.current_day = self.current_second
        
        self.second_count = 0
        self.hour_count = 0
        self.day_count = 0
    
    def check_limit(self) -> None:
        """Check and enforce rate limits."""
        now = datetime.now()
        
        # Reset counters if time windows have passed
        if now - self.current_second > timedelta(seconds=1):
            self.second_count = 0
            self.current_second = now
            
        if now - self.current_hour > timedelta(hours=1):
            self.hour_count = 0
            self.current_hour = now
            
        if now - self.current_day > timedelta(days=1):
            self.day_count = 0
            self.current_day = now
        
        # Check limits
        if any([
            self.second_count >= self.max_per_second,
            self.hour_count >= self.max_per_hour,
            self.day_count >= self.max_per_day
        ]):
            wait_time = self._calculate_wait_time()
            logging.warning(f"Rate limit reached. Waiting {wait_time} seconds")
            time.sleep(wait_time)
            
        # Increment counters
        self.second_count += 1
        self.hour_count += 1
        self.day_count += 1
    
    def _calculate_wait_time(self) -> float:
        """Calculate the time to wait before next send."""
        if self.second_count >= self.max_per_second:
            return 1.0
        if self.hour_count >= self.max_per_hour:
            return (self.current_hour + timedelta(hours=1) - datetime.now()).total_seconds()
        return (self.current_day + timedelta(days=1) - datetime.now()).total_seconds() 