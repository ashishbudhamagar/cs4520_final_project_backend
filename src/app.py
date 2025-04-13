from litestar import Litestar
from litestar.config.cors import CORSConfig

from routes.login_and_register import Controller_LoginAndRegister
from routes.user import Controller_User

from setupDatabase import setupDatabase


setupDatabase()



app = Litestar(

    cors_config=CORSConfig(allow_origins=["http://127.0.0.1:5500"]),
    route_handlers= [

        Controller_LoginAndRegister,
        Controller_User
        
    ]
    
)