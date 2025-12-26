"""Timing utilities for performance tracking."""

import time
from typing import Optional


class Timer:
    """Simple timer for measuring elapsed time."""
    
    def __init__(self):
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
    
    def start(self):
        """Start the timer."""
        self._start_time = time.time()
        self._end_time = None
    
    def stop(self):
        """Stop the timer."""
        if self._start_time is None:
            raise RuntimeError("Timer not started")
        self._end_time = time.time()
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self._start_time is None:
            raise RuntimeError("Timer not started")
        
        end = self._end_time if self._end_time else time.time()
        return end - self._start_time
    
    def elapsed_str(self) -> str:
        """Get elapsed time as formatted string."""
        elapsed = self.elapsed()
        
        if elapsed < 60:
            return f"{elapsed:.2f}s"
        elif elapsed < 3600:
            mins = int(elapsed // 60)
            secs = elapsed % 60
            return f"{mins}m {secs:.1f}s"
        else:
            hours = int(elapsed // 3600)
            mins = int((elapsed % 3600) // 60)
            return f"{hours}h {mins}m"
