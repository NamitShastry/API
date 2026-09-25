"""AeroIndex / FareOS — FastAPI Application Entrypoint."""

from __future__ import annotations

import asyncio
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.websocket import router as ws_router
from app.api.v1.router import api_v1_router
from app.collector.heartbeat import HeartbeatTracker
from app.collector.simulator import CalibratedSimulatorAdapter
from app.core.config import DataMode, settings
from app.services.pipeline_service import PipelineService


async def background_simulation_loop():
    """Background simulator task providing continuous live observations in SIMULATED_LIVE mode."""
    sim = CalibratedSimulatorAdapter(seed=settings.sim_seed)
    routes = ["DEL-BOM", "BOM-DEL", "DEL-BLR", "BLR-DEL", "BOM-BLR", "DEL-HYD", "BOM-GOI"]
    buckets = ["L01", "L03", "L07", "L14", "L21"]

    while True:
        try:
            # Heartbeats
            HeartbeatTracker.record_heartbeat("api", "HEALTHY")
            HeartbeatTracker.record_heartbeat("collector", "HEALTHY")
            HeartbeatTracker.record_heartbeat("worker", "HEALTHY")
            HeartbeatTracker.record_heartbeat("scheduler", "HEALTHY")
            HeartbeatTracker.record_heartbeat("postgres", "HEALTHY")
            HeartbeatTracker.record_heartbeat("redis", "HEALTHY")

            if settings.data_mode in (DataMode.SIMULATED_LIVE, DataMode.LIVE):
                # Pick randomized route and advance day
                import random
                r = random.choice(routes)
                b = random.choice(buckets)
                days_adv = {"L01": 1, "L03": 2, "L07": 5, "L14": 10, "L21": 18}[b]
                travel_date = datetime.date.today() + datetime.timedelta(days=days_adv)

                # Fetch quotes and ingest into pipeline
                quotes = await sim.fetch_quotes(r, b, travel_date, count=2)
                await PipelineService.ingest_live_observations(quotes)

            await asyncio.sleep(settings.simulation_interval_seconds)
        except asyncio.CancelledError:
            break
        except Exception as e:
            await asyncio.sleep(settings.simulation_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: register initial heartbeats
    HeartbeatTracker.record_heartbeat("api", "HEALTHY")
    HeartbeatTracker.record_heartbeat("collector", "HEALTHY")

    # Start simulation loop in background
    sim_task = asyncio.create_task(background_simulation_loop())

    yield

    # Shutdown
    sim_task.cancel()
    try:
        await sim_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.app_name,
    description="Real-Time Airfare Price Intelligence & Daily Index Platform for India",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_v1_router)
app.include_router(ws_router)

# Mount frontend static files
import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

web_public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../web/public"))

if os.path.exists(web_public_dir):
    app.mount("/static", StaticFiles(directory=web_public_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(web_public_dir, "index.html"))

    @app.get("/styles.css")
    async def serve_css():
        return FileResponse(os.path.join(web_public_dir, "styles.css"))

    @app.get("/app.js")
    async def serve_js():
        return FileResponse(os.path.join(web_public_dir, "app.js"))
else:
    @app.get("/")
    async def root():
        return {
            "platform": settings.app_name,
            "status": "OPERATIONAL",
            "data_mode": settings.data_mode.value,
            "docs": "/docs",
            "version": "1.0.0",
            "realtime_ws": "/ws/live",
        }

