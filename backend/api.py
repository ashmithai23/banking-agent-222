"""FastAPI web backend for VectraBank Agentic RAG.

Run:  uvicorn api:app --reload --port 8000   (from the backend/ directory)
"""

import asyncio
import json
import logging
import os
import io
import sys
from datetime import datetime
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from main_starter import BASE_DIR, EnhancedBankingSequentialOrchestration
from offline_agents import AGENT_NAMES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("vectrabank.api")

ALL_COLLECTIONS = [
    "fraud_detection", "loan_policies", "customer_support",
    "risk_assessment", "transaction_monitoring", "compliance",
]

SAMPLE_QUERIES = {
    "12345": "I need comprehensive financial planning including investments and retirement options",
    "67890": "I want to apply for a home loan and need to understand my eligibility",
    "11111": "I noticed some suspicious activity on my account and need help resolving it",
}

app = FastAPI(title="VectraBank Agentic RAG API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

system: Optional[EnhancedBankingSequentialOrchestration] = None
reports: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
MAX_REPORTS = 100


class AnalyzeRequest(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=50)
    query: str = Field(..., min_length=3, max_length=2000)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    collections: Optional[List[str]] = None
    top_k: int = Field(default=3, ge=1, le=10)


def get_system() -> EnhancedBankingSequentialOrchestration:
    if system is None:
        raise HTTPException(status_code=503, detail="System is still initializing")
    return system


def _store_report(report_dict: Dict[str, Any]) -> None:
    reports[report_dict["report_id"]] = report_dict
    while len(reports) > MAX_REPORTS:
        reports.popitem(last=False)


@app.on_event("startup")
async def startup() -> None:
    global system
    logger.info("Initializing banking orchestration system...")
    system = EnhancedBankingSequentialOrchestration()
    await system.get_customer_profiles()
    await system.load_enhanced_documents()
    logger.info(f"System ready (LLM mode: {system.llm_mode})")


# ----------------------------------------------------------------------------- meta

@app.get("/api/health")
async def health() -> Dict[str, Any]:
    s = get_system()
    stats = await s.chroma_store.get_collection_stats()
    return {
        "status": "ok",
        "llm_mode": s.llm_mode,
        "llm_model": s.llm_model,
        "sql_connected": bool(s.data_connector.connection_string),
        "documents": len(s.blob_connector.list_documents()),
        "chunks": sum(v.get("document_count", 0) for v in stats.values()),
        "agents": AGENT_NAMES,
    }


@app.get("/api/metrics")
async def metrics() -> Dict[str, Any]:
    s = get_system()
    return {
        "system": s.shared_state.get_system_metrics(),
        "performance": s.performance_metrics,
        "collections": await s.chroma_store.get_collection_stats(),
        "reports_stored": len(reports),
    }


# ----------------------------------------------------------------------------- customers

@app.get("/api/customers")
async def list_customers() -> List[Dict[str, Any]]:
    profiles = await get_system().get_customer_profiles()
    out = []
    for cid, p in profiles.items():
        d = p.model_dump()
        d["sample_query"] = SAMPLE_QUERIES.get(cid, "")
        d["computed_risk_score"] = get_system()._calculate_enhanced_risk_score(p, [])
        d["computed_risk_tier"] = get_system()._determine_risk_tier(d["computed_risk_score"])
        out.append(d)
    return out


@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str) -> Dict[str, Any]:
    s = get_system()
    profiles = await s.get_customer_profiles()
    if customer_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    d = profiles[customer_id].model_dump()
    d["interactions"] = s.shared_state.get_customer_interactions(customer_id)
    return d


# ----------------------------------------------------------------------------- documents / RAG

@app.get("/api/documents")
async def list_documents() -> List[Dict[str, Any]]:
    blob = get_system().blob_connector
    return [{"name": n, **(blob.get_document_metadata(n) or {})} for n in blob.list_documents()]


@app.get("/api/documents/{name}")
async def get_document(name: str) -> Dict[str, Any]:
    blob = get_system().blob_connector
    if name not in blob.list_documents():
        raise HTTPException(status_code=404, detail="Document not found")
    return {"name": name, "metadata": blob.get_document_metadata(name), "content": blob.get_document_content(name)}


@app.post("/api/search")
async def search(req: SearchRequest) -> List[Dict[str, Any]]:
    collections = [c for c in (req.collections or ALL_COLLECTIONS) if c in ALL_COLLECTIONS]
    if not collections:
        raise HTTPException(status_code=400, detail="No valid collections requested")
    results = await get_system().chroma_store.hybrid_search(req.query, collections, top_k=req.top_k)
    return [
        {
            "filename": r.get("filename"),
            "collection": r.get("collection"),
            "chunk_info": r.get("chunk_info"),
            "relevance_score": round(float(r.get("relevance_score", 0)), 4),
            "keyword_boost": round(float(r.get("keyword_boost", 0)), 4),
            "final_score": round(float(r.get("final_score", 0)), 4),
            "document": r.get("document"),
        }
        for r in results
    ]


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload custom policy document (.pdf, .md, .txt), extract text, and index into ChromaDB."""
    s = get_system()
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")
        
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    content = ""
    if filename.lower().endswith(".pdf"):
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
        except Exception as pdf_err:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF document: {pdf_err}")
    else:
        content = raw_bytes.decode("utf-8", errors="replace")

    if not content.strip():
        raise HTTPException(status_code=400, detail="Document contains no readable text")

    collection = s.chroma_store.determine_collection(filename, content)
    metadata = {
        "type": collection.replace("_policies", "").replace("_detection", ""),
        "version": "1.0",
        "effective_date": datetime.now().strftime("%Y-%m-%d"),
        "department": "Uploaded Policy",
        "filename": filename
    }

    # Store in blob/file registry
    s.blob_connector.upload_custom_document(filename, content, metadata)

    # Chunk & store in ChromaDB
    chunks_stored = await s.chroma_store.chunk_and_store_document(filename, content, collection)

    # Refresh policy definitions
    s.banking_policies = s._load_enhanced_policies()

    return {
        "status": "ok",
        "filename": filename,
        "collection": collection,
        "chunks": chunks_stored,
        "size_bytes": len(raw_bytes),
        "message": f"Successfully indexed {chunks_stored} chunks into collection '{collection}'"
    }


# ----------------------------------------------------------------------------- analysis

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    try:
        report = await get_system().run_enhanced_analysis(req.customer_id.strip(), req.query.strip())
    except Exception as e:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    d = report.model_dump()
    _store_report(d)
    return d


@app.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest) -> StreamingResponse:
    """Server-Sent Events stream of agent progress followed by the final report."""
    s = get_system()
    queue: "asyncio.Queue[Optional[Dict[str, Any]]]" = asyncio.Queue()

    async def worker() -> None:
        try:
            report = await s.run_enhanced_analysis(
                req.customer_id.strip(), req.query.strip(), on_event=queue.put_nowait
            )
            d = report.model_dump()
            _store_report(d)
            await queue.put({"type": "report", "report": d})
        except Exception as e:
            logger.exception("Streaming analysis failed")
            await queue.put({"type": "error", "message": str(e)})
        finally:
            await queue.put(None)

    async def event_source():
        task = asyncio.create_task(worker())
        yield f"data: {json.dumps({'type': 'start', 'agents': AGENT_NAMES, 'llm_mode': s.llm_mode})}\n\n"
        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield f"data: {json.dumps(event, default=str)}\n\n"
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/reports")
async def list_reports() -> List[Dict[str, Any]]:
    return [
        {
            "report_id": r["report_id"],
            "customer_id": r["customer_id"],
            "query": r["query"],
            "risk_assessment": r["risk_assessment"],
            "risk_score": r["risk_score"],
            "generated_at": r["generated_at"],
            "processing_time": r["processing_metrics"].get("total_processing_time_seconds"),
        }
        for r in reversed(reports.values())
    ]


@app.get("/api/reports/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")
    return reports[report_id]


# ----------------------------------------------------------------------------- static frontend

FRONTEND_DIST = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = os.path.realpath(os.path.join(FRONTEND_DIST, full_path))
        if full_path and candidate.startswith(os.path.realpath(FRONTEND_DIST) + os.sep) and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
