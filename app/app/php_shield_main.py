"""
PHP Shield API -- standalone service entrypoint.

    uvicorn app.php_shield_main:app --host 0.0.0.0 --port $PORT

Deliberately imports nothing from app.main / app.database, so it can boot (and fail) on its
own. Startup: validate config (production refuses to boot if anything required is missing),
connect to PHP Shield's own Supabase project, and run a write+delete self-test.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.php_shield import api, billing, config, netsafe, orders, services
from app.php_shield.ops import WriteFailed, health_report, startup_selftest
from app.php_shield.ratelimit import Busy, RateLimited

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("php_shield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    report = config.validate_startup()  # raises in production if required config is missing
    for w in report.warnings:
        log.warning("config: %s", w)
    if report.missing:
        log.error("config: missing %s (development mode, continuing)", ", ".join(report.missing))
    svc = services.init_services()
    try:
        startup_selftest(svc.store)
        log.info("startup self-test passed (write + delete)")
    except Exception:
        log.exception("startup self-test FAILED")
        if config.is_production():
            raise RuntimeError("PHP Shield refusing to start: database self-test failed") from None
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="PHP Shield API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=config.allowed_origins(), allow_methods=["GET", "POST", "OPTIONS"],
                       allow_headers=["Content-Type", "X-Admin-Key"], expose_headers=["Retry-After"], max_age=600)

    @app.exception_handler(RateLimited)
    async def _rate(_: Request, e: RateLimited):
        return JSONResponse({"detail": "Too many requests. Please try again later."}, status_code=429,
                            headers={"Retry-After": str(e.retry_after)})

    @app.exception_handler(Busy)
    async def _busy(_: Request, e: Busy):
        return JSONResponse({"detail": "The scanner is busy. Please try again in a moment."}, status_code=503,
                            headers={"Retry-After": str(Busy.retry_after)})

    @app.exception_handler(WriteFailed)
    async def _wf(_: Request, e: WriteFailed):
        return JSONResponse({"detail": "We couldn't save that right now. The team has been alerted - please try again shortly."},
                            status_code=503)

    for exc in (orders.OrderError, billing.BillingError):
        @app.exception_handler(exc)
        async def _err(_: Request, e):
            return JSONResponse({"detail": str(e)}, status_code=e.status_code)

    @app.exception_handler(netsafe.UnsafeURL)
    async def _unsafe(_: Request, e: netsafe.UnsafeURL):
        return JSONResponse({"detail": f"That URL can't be used: {e}"}, status_code=400)

    app.include_router(api.router)
    app.include_router(api.admin_router)

    @app.get("/health")
    def health():
        try:
            rep = health_report(services.get())
        except RuntimeError:
            return JSONResponse({"ok": False, "detail": "services not initialised"}, status_code=503)
        return JSONResponse(rep, status_code=200 if rep["ok"] else 503)

    return app


app = create_app()
