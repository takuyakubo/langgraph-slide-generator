"""
Error handling utilities for the LangGraph Slide Generator.
"""

import time
import logging
import traceback
from functools import wraps
from contextlib import contextmanager
from typing import Callable, Tuple, List, Any, Dict, Optional, Type, Union

from ..exceptions import SlideGeneratorError

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, 
          initial_delay: float = 1.0, 
          backoff: float = 2.0, 
          exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Decorator to retry a function on exception with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before retrying
        backoff: Multiplier for the delay after each attempt
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = initial_delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"All {max_attempts} retry attempts failed for {func.__name__}")
                        raise
                    
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} "
                        f"after error: {str(e)}. Waiting {current_delay}s."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
                    
        return wrapper
    return decorator

@contextmanager
def error_handling(error_type: Type[SlideGeneratorError], error_message: str):
    """
    Context manager for error handling and logging.
    
    Args:
        error_type: The type of SlideGeneratorError to raise
        error_message: Error message prefix
        
    Yields:
        None
    
    Raises:
        SlideGeneratorError: Wrapped exception with detailed message
    """
    try:
        yield
    except Exception as e:
        logger.error(
            f"{error_message}: {str(e)}\n{traceback.format_exc()}"
        )
        raise error_type(f"{error_message}: {str(e)}") from e

class CircuitBreakerOpenError(SlideGeneratorError):
    """Exception raised when a circuit breaker is open."""
    pass

class CircuitBreaker:
    """
    Implementation of the circuit breaker pattern.
    
    The circuit breaker prevents repeated calls to failing services by
    tracking failure rates and opening the circuit when too many failures
    occur in a short time.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Time in seconds before trying to close the circuit again
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function
            
        Raises:
            CircuitBreakerOpenError: If the circuit is open
            Exception: Any exception raised by the function
        """
        current_time = time.time()
        
        # OPEN state transitions to HALF-OPEN after the recovery timeout
        if self.state == "OPEN" and current_time - self.last_failure_time > self.recovery_timeout:
            self.state = "HALF-OPEN"
            logger.info("Circuit breaker transitioned to HALF-OPEN state")
        
        # If the circuit is OPEN, skip execution and raise an error
        if self.state == "OPEN":
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            # In HALF-OPEN state, a successful call closes the circuit
            if self.state == "HALF-OPEN":
                self.reset()
                logger.info("Circuit breaker transitioned to CLOSED state")
                
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = current_time
            
            # Open the circuit if failure threshold is reached or in HALF-OPEN state
            if (self.state == "CLOSED" and self.failure_count >= self.failure_threshold) or self.state == "HALF-OPEN":
                self.state = "OPEN"
                logger.warning(f"Circuit breaker transitioned to OPEN state after {self.failure_count} failures")
            
            raise
    
    def reset(self) -> None:
        """Reset the circuit breaker to its initial state."""
        self.failure_count = 0
        self.state = "CLOSED"
