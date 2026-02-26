import sys
import time
import tracemalloc
from typing import Any, Set, Callable, TypeVar
from functools import wraps

# ============================================================================
# Memory Utilities
# ============================================================================

def get_deep_size(obj: Any, seen: Set[int] = None) -> int:
    """Calculate deep size of Python objects including nested structures."""
    if seen is None:
        seen = set()
    
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    
    size = sys.getsizeof(obj)
    
    if isinstance(obj, dict):
        size += sum(get_deep_size(k, seen) + get_deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(get_deep_size(item, seen) for item in obj)
    
    return size


def format_memory(num_bytes: int) -> str:
    """Format bytes into human-readable units: bytes, MB, MiB."""
    mb = num_bytes / 1_000_000
    mib = num_bytes / 1_048_576
    return f"{num_bytes} bytes ({mb:.6f} MB, {mib:.6f} MiB)"


def format_time(seconds: float) -> str:
    """Format seconds into human-readable time units."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1_000:.4f} ms"
    else:
        return f"{seconds:.4f} s"


# ============================================================================
# Profiler Decorator
# ============================================================================

F = TypeVar('F', bound=Callable[..., Any])


def profile_function(func: F) -> F:
    """
    Decorator to profile a function:
    - Execution time
    - Memory usage (peak memory during execution)
    - Object-level memory for returned value
    
    Usage:
        @profile_function
        def my_func():
            return [1, 2, 3]
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Start memory tracking
        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # End timing and memory tracking
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Format output
        func_name = func.__name__
        exec_time = end_time - start_time
        result_size = get_deep_size(result) if result is not None else 0
        
        print(f"\n{'='*70}")
        print(f"Profile: {func_name}")
        print(f"{'='*70}")
        print(f"Execution Time  : {format_time(exec_time)}")
        print(f"Peak Memory     : {format_memory(peak)}")
        print(f"Result Size     : {format_memory(result_size)}")
        print(f"{'='*70}\n")
        
        return result
    
    return wrapper


# ============================================================================
# Context Manager for Manual Profiling
# ============================================================================

class Profiler:
    """
    Context manager to profile code blocks inside notebooks.
    
    Usage:
        with Profiler("My Operation"):
            # code to profile
            result = expensive_function()
    """
    def __init__(self, name: str = "Code Block"):
        self.name = name
        self.start_time = None
        self.peak_memory = None
    
    def __enter__(self):
        tracemalloc.start()
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        exec_time = end_time - self.start_time
        self.peak_memory = peak
        
        print(f"\n{'='*70}")
        print(f"Profile: {self.name}")
        print(f"{'='*70}")
        print(f"Execution Time  : {format_time(exec_time)}")
        print(f"Peak Memory     : {format_memory(peak)}")
        print(f"{'='*70}\n")
        
        return False


# ============================================================================
# Manual Profiler Functions
# ============================================================================

def print_object_memory(name: str, obj: Any) -> None:
    """Print memory usage of a single object."""
    print(f"{name} memory: {format_memory(get_deep_size(obj))}")


def compare_objects(*objects: tuple[str, Any]) -> None:
    """
    Compare memory usage of multiple objects.
    
    Usage:
        compare_objects(("list_a", [1, 2, 3]), ("dict_b", {"x": 1}))
    """
    print(f"\n{'='*70}")
    print("Object Memory Comparison")
    print(f"{'='*70}")
    for name, obj in objects:
        size = get_deep_size(obj)
        print(f"{name:20s} : {format_memory(size)}")
    print(f"{'='*70}\n")


# ============================================================================
# Quick Profiler Utility
# ============================================================================

def quick_profile(func: Callable, *args, **kwargs) -> Any:
    """
    Quick profiler for one-off function calls.
    
    Usage:
        result = quick_profile(my_function, arg1, arg2, kwarg=value)
    """
    return profile_function(func)(*args, **kwargs)
