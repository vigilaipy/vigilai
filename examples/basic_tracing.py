from vigilai import Inspector
import time


def main() -> None:
    # Initialize the Inspector
    ins = Inspector(model="gpt-4o", provider="openai")

    print("Running LLM trace example...")

    # 1. Wrap your LLM call in a trace
    with ins.trace("generate_welcome_message", metadata={"user_id": 123}):
        # Simulate LLM latency
        time.sleep(0.5)

        # Simulate token usage and cost calculation
        ins.cost_tracker.add_usage(prompt_tokens=150, completion_tokens=50)

        print("Generated welcome message successfully!")

    # 2. Print summary stats
    stats = ins.stats()
    print(f"Stats: {stats}")

    # 3. Generate HTML report
    report_path = ins.report()
    print(f"Report generated at: {report_path}")


if __name__ == "__main__":
    main()
