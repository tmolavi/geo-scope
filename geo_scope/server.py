"""
FastAPI Server for GEO-Scope (AI Visibility & Algorithm Reverse-Engineering Platform)
"""

import asyncio
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from geo_scope.engine.query_generator import generate_prompt_dataset, INDUSTRY_PRESETS
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.feature_extractor import parse_model_response
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.strategy_builder import generate_geo_playbook
from geo_scope.engine.export_manager import export_records_to_csv, export_citations_to_csv, export_full_json

app = FastAPI(
    title="GEO-Scope API",
    description="Generative Engine Optimization (GEO) & AI Algorithm Reverse Engineering Engine",
    version="1.0.0"
)

# In-memory session state
STATE = {
    "is_running": False,
    "progress": 0,
    "total_tasks": 0,
    "current_status": "Ready",
    "prompts": [],
    "raw_responses": [],
    "parsed_records": [],
    "analysis_results": None,
    "playbook": None,
    "target_brand": "HubSpot",
    "competitors": ["Salesforce", "Zoho CRM", "Pipedrive", "Monday CRM"]
}

# Mount static folder
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class BenchmarkRequest(BaseModel):
    niche_key: str = "crm_sales"
    target_brand: Optional[str] = "HubSpot"
    competitors: Optional[List[str]] = None
    language: str = "both"  # "fa", "en", "both"
    prompt_count: int = 1000
    models: Optional[List[str]] = ["perplexity_sonar", "chatgpt_search", "gemini_grounding", "claude_3_7"]
    custom_topic: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>GEO-Scope Server Running</h1>"


@app.get("/api/presets")
async def get_presets():
    return {
        "presets": INDUSTRY_PRESETS,
        "available_models": [
            {"id": "perplexity_sonar", "name": "Perplexity (Sonar Pro Search)", "icon": "⚡", "bias": "Reddit & UGC heavy"},
            {"id": "chatgpt_search", "name": "ChatGPT Search (GPT-4o)", "icon": "🟢", "bias": "Bing Index & High-DR PR"},
            {"id": "gemini_grounding", "name": "Google Gemini (Search Grounding)", "icon": "🔵", "bias": "Google Index & Knowledge Graph"},
            {"id": "claude_3_7", "name": "Anthropic Claude 3.7", "icon": "🟣", "bias": "Analytical synthesis & review consensus"}
        ]
    }


def execute_pipeline_sync(req: BenchmarkRequest):
    """
    Executes the entire 1000-prompt pipeline in background.
    """
    STATE["is_running"] = True
    STATE["progress"] = 0
    STATE["current_status"] = "Generating 1,000 Prompt Variations across Intent Categories..."
    
    brand = req.target_brand.strip() if req.target_brand else "HubSpot"
    preset = INDUSTRY_PRESETS.get(req.niche_key, INDUSTRY_PRESETS["crm_sales"])
    comps = req.competitors if req.competitors and len(req.competitors) > 0 else preset["competitors"]
    
    STATE["target_brand"] = brand
    STATE["competitors"] = comps

    # 1. Generate Prompts
    prompts = generate_prompt_dataset(
        niche_key=req.niche_key,
        target_brand=brand,
        competitors=comps,
        language=req.language,
        total_count=req.prompt_count,
        custom_topic=req.custom_topic
    )
    STATE["prompts"] = prompts

    # 2. Run Models
    STATE["current_status"] = f"Executing queries across {len(req.models)} AI engines..."
    runner = ModelRunner()
    
    async def run_async():
        def progress_cb(done, total):
            STATE["progress"] = int((done / total) * 100)
            STATE["current_status"] = f"Processed {done}/{total} AI query inferences ({STATE['progress']}%)"

        return await runner.execute_batch(prompts, models=req.models, progress_callback=progress_cb)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    raw_responses = loop.run_until_complete(run_async())
    loop.close()
    
    STATE["raw_responses"] = raw_responses

    # 3. Parse and Extract Features
    STATE["current_status"] = "Extracting Brand Mentions, Ranks, and Citation Graph..."
    parsed = []
    for item in raw_responses:
        q_item = item["query_item"]
        model = item["model"]
        text = item["response_text"]
        p_record = parse_model_response(q_item, model, text)
        p_record["full_response_text"] = text
        p_record["query_text"] = q_item["query"]
        parsed.append(p_record)
    STATE["parsed_records"] = parsed

    # 4. Run Algorithmic Reverse Engineering Analysis
    STATE["current_status"] = "Reverse-engineering Ranking Factor Weights and Calculating Share of Model..."
    analyzer = AlgoAnalyzer(parsed, brand, comps)
    analysis = analyzer.compute_full_analysis()
    STATE["analysis_results"] = analysis

    # 5. Build Actionable Strategic Playbook
    STATE["current_status"] = "Synthesizing Custom GEO Action Roadmap..."
    playbook = generate_geo_playbook(analysis)
    STATE["playbook"] = playbook

    STATE["current_status"] = "Completed Successfully"
    STATE["progress"] = 100
    STATE["is_running"] = False


@app.post("/api/run_benchmark")
async def run_benchmark(req: BenchmarkRequest, background_tasks: BackgroundTasks):
    if STATE["is_running"]:
        return {"status": "already_running", "message": "A benchmark is already in progress."}
    
    background_tasks.add_task(execute_pipeline_sync, req)
    return {"status": "started", "message": f"Started {req.prompt_count} prompt analysis across selected models."}


@app.get("/api/benchmark_status")
async def get_status():
    return {
        "is_running": STATE["is_running"],
        "progress": STATE["progress"],
        "status_text": STATE["current_status"],
        "has_results": STATE["analysis_results"] is not None,
        "total_prompts": len(STATE["prompts"]),
        "total_records": len(STATE["parsed_records"])
    }


@app.get("/api/benchmark_results")
async def get_results():
    if not STATE["analysis_results"]:
        raise HTTPException(status_code=404, detail="No benchmark results available yet.")
    return {
        "analysis": STATE["analysis_results"],
        "playbook": STATE["playbook"],
        "summary": STATE["analysis_results"]["summary"]
    }


@app.get("/api/prompts")
async def get_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    intent: Optional[str] = None,
    target_mentioned: Optional[bool] = None,
    search: Optional[str] = None
):
    records = STATE["parsed_records"]
    if not records:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    grouped = {}
    for r in records:
        qid = r["query_id"]
        if qid not in grouped:
            grouped[qid] = {
                "query_id": qid,
                "query_text": r.get("query_text", ""),
                "intent": r.get("intent", ""),
                "language": r.get("language", ""),
                "models_data": {}
            }
        grouped[qid]["models_data"][r["model"]] = {
            "mentioned": r.get("target_mentioned", False),
            "rank": r.get("target_rank", 0),
            "is_top_1": r.get("target_is_top_1", False),
            "sentiment": r.get("target_sentiment", "neutral"),
            "citations": r.get("citations", []),
            "response_text": r.get("full_response_text", "")
        }

    items_list = list(grouped.values())

    if intent and intent != "all":
        items_list = [it for it in items_list if it["intent"] == intent]
    if search:
        search_lower = search.lower()
        items_list = [it for it in items_list if search_lower in it["query_text"].lower()]
    if target_mentioned is not None:
        items_list = [
            it for it in items_list
            if any(m["mentioned"] == target_mentioned for m in it["models_data"].values())
        ]

    total_count = len(items_list)
    start_idx = (page - 1) * page_size
    paginated = items_list[start_idx:start_idx + page_size]

    return {
        "items": paginated,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size
    }


@app.get("/api/export/{export_type}")
async def export_data(export_type: str):
    if not STATE["parsed_records"]:
        raise HTTPException(status_code=404, detail="No data available to export.")

    if export_type == "records_csv":
        csv_content = export_records_to_csv(STATE["parsed_records"])
        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=geo_queries_benchmark.csv"})
    elif export_type == "citations_csv":
        csv_content = export_citations_to_csv(STATE["parsed_records"])
        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=geo_citations_graph.csv"})
    elif export_type == "full_json":
        json_content = export_full_json(STATE["analysis_results"], STATE["prompts"])
        return Response(content=json_content, media_type="application/json", headers={"Content-Disposition": "attachment; filename=geo_full_intelligence.json"})
    else:
        raise HTTPException(status_code=400, detail="Invalid export type.")


def initialize_default_dataset():
    req = BenchmarkRequest(
        niche_key="crm_sales",
        target_brand="HubSpot",
        competitors=["Salesforce", "Zoho CRM", "Pipedrive", "Monday CRM"],
        language="both",
        prompt_count=1000
    )
    execute_pipeline_sync(req)


# Run default benchmark on startup
initialize_default_dataset()
