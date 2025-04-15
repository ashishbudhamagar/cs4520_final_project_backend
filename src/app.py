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



app = Litestar(

    cors_config=CORSConfig(allow_origins=["http://127.0.0.1:5500"]),
    route_handlers= [
        Controller_LoginAndRegister,
        Controller_User,
        Controller_Post,
        Controller_Caption
    ],
    static_files_config=[
        StaticFilesConfig(
            directories=[Path("user_post_images")],
            path="/images"
        )
    ]
)

