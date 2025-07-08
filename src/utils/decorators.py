"""
Utility decorators for FlowState-CLI.
Provides retry logic, timing, and validation decorators.
"""

import time
import functools
from typing import Callable, Any, Optional, Type, Tuple
from .exceptions import FlowStateError


def retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float = 60.0
) -> Callable:
    """
    Retry decorator with exponential backoff.
    
    Args:
        exceptions: Tuple of exceptions to catch
        attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplication factor for delay
        max_delay: Maximum delay between retries
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < attempts - 1:
                        time.sleep(current_delay)
                        current_delay = min(current_delay * backoff, max_delay)
                    else:
                        # Last attempt failed
                        if isinstance(e, FlowStateError):
                            raise
                        else:
                            raise FlowStateError(
                                f"{func.__name__} failed after {attempts} attempts",
                                details={'last_error': str(e)}
                            ) from e
            
            # Should never reach here
            raise last_exception
        
        return wrapper
    return decorator


def timed(prefix: str = "") -> Callable:
    """
    Timing decorator for performance monitoring.
    
    Args:
        prefix: Optional prefix for timing message
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                message = f"{prefix} " if prefix else ""
                message += f"{func.__name__} took {elapsed:.2f}s"
                print(message)
        
        return wrapper
    return decorator


def validate_input(validator_func: Callable[[Any], bool], 
                  error_message: str = "Invalid input") -> Callable:
    """
    Input validation decorator.
    
    Args:
        validator_func: Function that returns True if input is valid
        error_message: Error message if validation fails
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Validate first positional argument
            if args and not validator_func(args[0]):
                raise ValueError(f"{error_message}: {args[0]}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def ensure_path_exists(create: bool = True) -> Callable:
    """
    Decorator to ensure path arguments exist.
    
    Args:
        create: Whether to create the path if it doesn't exist
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from pathlib import Path
            
            # Check first argument if it's a path
            if args and isinstance(args[0], (str, Path)):
                path = Path(args[0])
                if not path.exists():
                    if create and path.suffix == '':  # It's a directory
                        path.mkdir(parents=True, exist_ok=True)
                    elif not create:
                        raise FileNotFoundError(f"Path does not exist: {path}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def cached(ttl: Optional[int] = None) -> Callable:
    """
    Simple caching decorator with optional TTL.
    
    Args:
        ttl: Time-to-live in seconds (None for no expiration)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from arguments
            key = str(args) + str(kwargs)
            
            # Check if cached value exists and is still valid
            if key in cache:
                if ttl is None:
                    return cache[key]
                elif time.time() - cache_times[key] < ttl:
                    return cache[key]
            
            # Compute and cache the result
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = time.time()
            
            return result
        
        # Add cache control methods
        wrapper.clear_cache = lambda: (cache.clear(), cache_times.clear())
        wrapper.cache_info = lambda: {'size': len(cache), 'keys': list(cache.keys())}
        
        return wrapper
    return decorator