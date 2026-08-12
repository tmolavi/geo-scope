"""
Example 01: Quickstart Benchmark
Runs a fast 50-prompt test on a custom brand using Python API.
"""

from geo_scope import (
    generate_prompt_dataset,
    ModelRunner,
    parse_model_response,
    AlgoAnalyzer,
    generate_geo_playbook
)
import asyncio

async def main():
    print("⟠ Generating 50 test prompts for 'Notion' in Project Management...")
    prompts = generate_prompt_dataset(
        niche_key="project_management",
        target_brand="Notion",
        competitors=["Asana", "ClickUp", "Monday.com", "Trello"],
        language="both",
        total_count=50
    )

    runner = ModelRunner()
    print("Executing queries across Perplexity, ChatGPT Search, Gemini, and Claude...")
    responses = await runner.execute_batch(prompts)

    parsed = []
    for r in responses:
        item = parse_model_response(r["query_item"], r["model"], r["response_text"])
        parsed.append(item)

    analyzer = AlgoAnalyzer(parsed, "Notion", ["Asana", "ClickUp", "Monday.com", "Trello"])
    results = analyzer.compute_full_analysis()

    print("\n--- RESULTS SUMMARY ---")
    print(f"Overall Share of Model: {results['summary']['overall_sov']}%")
    print(f"Top-1 Rank Rate: {results['summary']['overall_top1_rate']}%")
    print(f"Best Performing Model: {results['summary']['best_performing_model']}")

if __name__ == "__main__":
    asyncio.run(main())
