"""
Background task execution module.
Provides async task handling with retry logic and status tracking.
"""

import os
import json
import time
import threading
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from .logging_config import log_info, log_error


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Task:
    id: str
    name: str
    status: TaskStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3


_task_store: Dict[str, Task] = {}
_executor: Optional[ThreadPoolExecutor] = None
_task_queue: Queue = Queue()


def get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        max_workers = int(os.environ.get("TASK_MAX_WORKERS", "4"))
        _executor = ThreadPoolExecutor(max_workers=max_workers)
    return _executor


def generate_task_id() -> str:
    return hashlib.sha256(f"{time.time()}{os.urandom(8).hex()}".encode()).hexdigest()[:16]


def create_task(name: str, max_retries: int = 3) -> Task:
    task = Task(
        id=generate_task_id(),
        name=name,
        status=TaskStatus.PENDING,
        created_at=datetime.now(timezone.utc).isoformat(),
        max_retries=max_retries,
    )
    _task_store[task.id] = task
    return task


def get_task(task_id: str) -> Optional[Task]:
    return _task_store.get(task_id)


def update_task(task: Task, **kwargs):
    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)


def execute_with_retry(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Dict[str, Any]:
    """Execute a function with exponential backoff retry."""
    kwargs = kwargs or {}
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            return {"success": True, "result": result, "attempts": attempt + 1}
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                delay = retry_delay * (backoff_factor ** attempt)
                log_info(f"Task retry {attempt + 1}/{max_retries}", 
                        function=func.__name__, delay=delay, error=str(e))
                time.sleep(delay)
    
    return {"success": False, "error": str(last_error), "attempts": max_retries + 1}


def run_async(func: Callable, *args, **kwargs) -> str:
    """Run a function asynchronously and return task ID."""
    task = create_task(func.__name__)
    
    def wrapper():
        update_task(task, status=TaskStatus.RUNNING, started_at=datetime.now(timezone.utc).isoformat())
        
        try:
            max_retries = kwargs.pop("_max_retries", 3)
            result = execute_with_retry(func, args, kwargs, max_retries=max_retries)
            
            if result["success"]:
                update_task(
                    task,
                    status=TaskStatus.COMPLETED,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    result=result["result"],
                    retries=result["attempts"] - 1,
                )
            else:
                update_task(
                    task,
                    status=TaskStatus.FAILED,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    error=result["error"],
                    retries=result["attempts"] - 1,
                )
        except Exception as e:
            log_error(f"Task {task.id} failed", exception=e)
            update_task(
                task,
                status=TaskStatus.FAILED,
                completed_at=datetime.now(timezone.utc).isoformat(),
                error=str(e),
            )
    
    executor = get_executor()
    executor.submit(wrapper)
    
    return task.id


def run_sync(func: Callable, *args, **kwargs) -> Any:
    """Run a function synchronously with retry logic."""
    max_retries = kwargs.pop("_max_retries", 3)
    result = execute_with_retry(func, args, kwargs, max_retries=max_retries)
    
    if result["success"]:
        return result["result"]
    raise Exception(result["error"])


class ExternalAPICaller:
    """Helper class for external API calls with retry and circuit breaker."""
    
    def __init__(
        self,
        timeout: int = 15,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self._failure_count = 0
        self._circuit_open = False
        self._circuit_opened_at: Optional[float] = None
    
    def _check_circuit(self) -> bool:
        if not self._circuit_open:
            return True
        
        if self._circuit_opened_at:
            elapsed = time.time() - self._circuit_opened_at
            if elapsed >= self.circuit_breaker_timeout:
                self._circuit_open = False
                self._failure_count = 0
                return True
        
        return False
    
    def _record_success(self):
        self._failure_count = 0
        self._circuit_open = False
    
    def _record_failure(self):
        self._failure_count += 1
        if self._failure_count >= self.circuit_breaker_threshold:
            self._circuit_open = True
            self._circuit_opened_at = time.time()
    
    def call(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        if not self._check_circuit():
            return {"success": False, "error": "Circuit breaker open"}
        
        result = execute_with_retry(
            func, args, kwargs,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
        )
        
        if result["success"]:
            self._record_success()
        else:
            self._record_failure()
        
        return result


def cleanup_old_tasks(max_age_hours: int = 24) -> int:
    """Remove old completed/failed tasks from store."""
    now = datetime.now(timezone.utc)
    to_remove = []
    
    for task_id, task in _task_store.items():
        if task.completed_at:
            completed = datetime.fromisoformat(task.completed_at.replace('Z', '+00:00'))
            age_hours = (now - completed).total_seconds() / 3600
            if age_hours > max_age_hours:
                to_remove.append(task_id)
    
    for task_id in to_remove:
        del _task_store[task_id]
    
    return len(to_remove)
