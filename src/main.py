import os
import logging 
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.logging import setup_logging
from database import engine, Base
from core.config import settings
from routes import auth, i18n
from utils import create_admin_user_on_startup

cwd = os.getcwd()
static_path = os.path.abspath(os.path.join(cwd, "static"))
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación y creando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    create_admin_user_on_startup()
    yield
    logger.info("Apagando aplicación...")


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
    expose_headers=settings.ALLOWED_EXPOSED_HEADERS,
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(auth.router, prefix="/auth")
app.include_router(i18n.router)
