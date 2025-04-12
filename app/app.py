from litestar import Litestar, get
from litestar.config.cors import CORSConfig

from modules.setup_database import setupDatabase

from modules.routes.login_and_register import Controller_LoginAndRegister
from modules.routes.user import Controller_User



corsConfig = CORSConfig(allow_origins=["http://127.0.0.1:5500"])
setupDatabase()



app = Litestar(cors_config=corsConfig, route_handlers=[Controller_LoginAndRegister, Controller_User])