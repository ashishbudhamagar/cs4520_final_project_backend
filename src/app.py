from litestar import Litestar
from litestar.config.cors import CORSConfig

from setupDatabase import setupDatabase

from routes.login_and_register import Controller_LoginAndRegister
from routes.user import Controller_User
from routes.post import Controller_Post
from routes.caption import Controller_Caption


from litestar.static_files.config import StaticFilesConfig
from pathlib import Path

setupDatabase()
BASE_DIR = Path(__file__).parent

# http://127.0.0.1:8000

app = Litestar(

    cors_config = CORSConfig(allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"], allow_methods=["*"], allow_headers=["*"]),
    route_handlers= [
        Controller_LoginAndRegister,
        Controller_User,
        Controller_Post,
        Controller_Caption
    ],
    static_files_config=[
        StaticFilesConfig(
            directories=[BASE_DIR / "user_post_images"],
            path="/images"
        )
    ]
)

