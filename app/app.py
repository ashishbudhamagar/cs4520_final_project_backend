from litestar import Litestar, get, post, status_codes, Controller
from litestar.exceptions import HTTPException
from litestar.config.cors import CORSConfig
import sqlite3



from modules.setup_database import setupDatabase
from modules.routes.login_and_register import Controller_LoginAndRegister




corsConfig = CORSConfig(allow_origins=["http://127.0.0.1:5500"])
setupDatabase()



@get('/')
async def index() -> str:
    return 'Hello asd'






app = Litestar(cors_config=corsConfig, route_handlers=[index, login, register])