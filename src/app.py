from litestar import Litestar
from litestar.config.cors import CORSConfig

from src.routes.login_and_register import Controller_LoginAndRegister

from src.setupDatabase import setupDatabase



setupDatabase()



app = Litestar(

    CORSConfig(allow_origins=["http://127.0.0.1:5500"]),

    route_handlers= [

        Controller_LoginAndRegister,


    ]
    
)