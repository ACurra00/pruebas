from api.endpoints import motivos
from api.endpoints import router_login
from api.endpoints import router_usuarios
from api.endpoints import router_person
from api.endpoints import router_carnet_activo
from api.endpoints import router_imprimir_carnet


from fastapi import APIRouter


# from api.endpoints.web.user import router as userRouter


api_router = APIRouter()

# EndPoints APP
# router.include_router(userRouter, prefix="/user", tags=["Users"])
api_router.include_router(motivos.router, prefix="/motivos", tags=["motivo"])
api_router.include_router(router_usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(router_login.router, prefix="/login", tags=["login"])
api_router.include_router(router_person.router, prefix="/person", tags=["persons"])
api_router.include_router(router_carnet_activo.router, prefix="/carnet_activo", tags=["carnets_activo"])
api_router.include_router(router_imprimir_carnet.router, prefix="/imprimir", tags=["imprimir_carnet_activo"])




