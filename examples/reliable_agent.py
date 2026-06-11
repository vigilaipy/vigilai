from vigilai import Inspector
from vigilai.reliability import FallbackChain, LoopGuard
import random

ins = Inspector()


# 1. Auto Retry Example
@ins.reliable(retries=3, timeout_sec=1)
def flaky_api_call() -> str:
    print("Attempting API call...")
    if random.random() < 0.7:
        raise ConnectionError("Network timeout!")
    return "API response successful"


# 2. Fallback Chain Example
def primary_model() -> str:
    raise RuntimeError("Primary model is down")


def fallback_model() -> str:
    return "Response from fallback model"


# 3. Infinite Loop Guard Example
def run_agent() -> None:
    guard = LoopGuard(max_iterations=5)

    while True:
        try:
            guard.tick()
            print(f"Agent iteration {guard.current_iteration}...")
        except RuntimeError as e:
            print(f"Agent stopped: {e}")
            break


def main() -> None:
    print("--- Retry ---")
    try:
        result = flaky_api_call()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Final failure: {e}")

    print("\n--- Fallback ---")
    chain = FallbackChain([primary_model, fallback_model])
    print(f"Result: {chain.execute()}")

    print("\n--- Loop Guard ---")
    run_agent()


if __name__ == "__main__":
    main()
