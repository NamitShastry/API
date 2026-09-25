from app.api.v1.endpoints import analytics, auth, health, index, quotes

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth.router)
api_v1_router.include_router(index.router)
api_v1_router.include_router(quotes.router)
api_v1_router.include_router(health.router)
api_v1_router.include_router(analytics.router)

