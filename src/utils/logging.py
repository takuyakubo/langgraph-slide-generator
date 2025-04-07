"""
Logging utilities for the LangGraph Slide Generator.
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, Any, Optional

def setup_logger(
    logger_name: str, 
    log_level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure a logger.
    
    Args:
        logger_name: Name of the logger
        log_level: Logging level (default: INFO)
        log_format: Custom log format (if None, a default format is used)
        log_file: Path to log file (if None, logs to console only)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Default format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Don't propagate to root logger
    logger.propagate = False
    
    return logger

def log_event(
    logger: logging.Logger,
    event_type: str,
    job_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    level: int = logging.INFO
) -> None:
    """
    Log a structured event with job details.
    
    Args:
        logger: Logger to use
        event_type: Type of event
        job_id: Job ID (if applicable)
        details: Additional event details
        level: Logging level
    """
    event_data = {
        "event_type": event_type,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    
    if job_id:
        event_data["job_id"] = job_id
        
    if details:
        event_data["details"] = details
    
    logger.log(level, json.dumps(event_data))

class ErrorMetrics:
    """
    Track error metrics for monitoring and analysis.
    """
    
    def __init__(self):
        """Initialize the error metrics collection."""
        from collections import defaultdict, deque
        import time
        
        self.error_counts = defaultdict(int)
        self.error_rates = defaultdict(list)
        self.last_errors = deque(maxlen=100)
        self.time = time  # Store time for consistent access
    
    def record_error(self, error_type: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an error occurrence.
        
        Args:
            error_type: Type of error
            context: Additional context information
        """
        self.error_counts[error_type] += 1
        self.last_errors.append({
            "type": error_type,
            "timestamp": self.time.time(),
            "context": context or {}
        })
    
    def record_operation(self, operation_type: str, success: bool) -> None:
        """
        Record an operation's success or failure.
        
        Args:
            operation_type: Type of operation
            success: Whether the operation succeeded
        """
        self.error_rates[operation_type].append(0 if success else 1)
        # Keep only the last 100 records
        if len(self.error_rates[operation_type]) > 100:
            self.error_rates[operation_type].pop(0)
    
    def get_error_rate(self, operation_type: str) -> float:
        """
        Calculate the error rate for an operation type.
        
        Args:
            operation_type: Type of operation
            
        Returns:
            Error rate as a float (0.0 to 1.0)
        """
        records = self.error_rates.get(operation_type, [])
        if not records:
            return 0.0
        return sum(records) / len(records)
    
    def get_most_common_errors(self, limit: int = 10) -> list:
        """
        Get the most common error types.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of (error_type, count) tuples
        """
        return sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
