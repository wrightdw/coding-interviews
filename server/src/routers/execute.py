"""Code execution routes."""

from fastapi import APIRouter, HTTPException, status
import time
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

from src.models import ExecuteRequest, ExecutionResult

router = APIRouter()


def execute_javascript(code: str, stdin: str, timeout: int) -> ExecutionResult:
    """Mock JavaScript execution (returns message about JS execution)."""
    return ExecutionResult(
        success=False,
        stdout="",
        stderr="JavaScript execution requires Node.js runtime (not implemented in mock)",
        exitCode=1,
        executionTime=0.0,
        error="JavaScript execution not available in backend mock"
    )


def execute_python(code: str, stdin: str, timeout: int) -> ExecutionResult:
    """Execute Python code safely."""
    start_time = time.time()
    
    try:
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create restricted globals
        restricted_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
            }
        }
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, restricted_globals)
        
        execution_time = (time.time() - start_time) * 1000
        
        return ExecutionResult(
            success=True,
            stdout=stdout_capture.getvalue(),
            stderr=stderr_capture.getvalue(),
            exitCode=0,
            executionTime=execution_time,
            error=None
        )
    
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        
        return ExecutionResult(
            success=False,
            stdout=stdout_capture.getvalue() if 'stdout_capture' in locals() else "",
            stderr=str(e),
            exitCode=1,
            executionTime=execution_time,
            error=str(e)
        )


def execute_java(code: str, stdin: str, timeout: int) -> ExecutionResult:
    """Mock Java execution."""
    return ExecutionResult(
        success=False,
        stdout="",
        stderr="Java execution requires JDK runtime (not implemented in mock)",
        exitCode=1,
        executionTime=0.0,
        error="Java execution not available in backend mock"
    )


def execute_cpp(code: str, stdin: str, timeout: int) -> ExecutionResult:
    """Mock C++ execution."""
    return ExecutionResult(
        success=False,
        stdout="",
        stderr="C++ execution requires GCC compiler (not implemented in mock)",
        exitCode=1,
        executionTime=0.0,
        error="C++ execution not available in backend mock"
    )


@router.post("/execute", response_model=ExecutionResult)
async def execute_code(request: ExecuteRequest):
    """Execute code in a sandboxed environment."""
    
    executors = {
        "javascript": execute_javascript,
        "python": execute_python,
        "java": execute_java,
        "cpp": execute_cpp,
    }
    
    executor = executors.get(request.language.value)
    
    if not executor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {request.language.value}"
        )
    
    try:
        result = executor(request.code, request.stdin, request.timeout)
        return result
    
    except Exception as e:
        return ExecutionResult(
            success=False,
            stdout="",
            stderr=str(e),
            exitCode=1,
            executionTime=0.0,
            error=str(e)
        )
