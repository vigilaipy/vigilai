import pytest
import time
from vigilai.reliability import retry, FallbackChain, LoopGuard

def test_retry_success() -> None:
    calls = 0
    
    @retry(retries=3, timeout_sec=0)
    def my_func() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ValueError("Fail")
        return "Success"
        
    result = my_func()
    assert result == "Success"
    assert calls == 3

def test_retry_failure() -> None:
    @retry(retries=2, timeout_sec=0)
    def always_fails() -> None:
        raise ValueError("Fail")
        
    with pytest.raises(RuntimeError, match="Failed after 2 retries"):
        always_fails()

def test_fallback_chain() -> None:
    def fail_func() -> str:
        raise ValueError("Fail")
        
    def success_func() -> str:
        return "Success"
        
    chain = FallbackChain([fail_func, success_func])
    assert chain.execute() == "Success"

def test_loop_guard() -> None:
    guard = LoopGuard(max_iterations=3)
    
    guard.tick()
    guard.tick()
    guard.tick()
    
    with pytest.raises(RuntimeError, match="Infinite loop detected"):
        guard.tick()
        
    guard.reset()
    guard.tick() # Should not raise
