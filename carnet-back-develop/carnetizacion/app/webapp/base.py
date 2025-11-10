from fastapi import APIRouter
from webapp.admin import router_admin
from webapp.admin.tipo_de_motivos import router_motivos_admin
from webapp.admin.tipo_de_motivos import router_motivos_crear
from webapp.admin.tipo_de_motivos.editar_tipo_motivo import router_edit_tipo_motivo
from webapp.admin.usuarios import router_edit_usuario
from webapp.admin.usuarios import router_form_usuarios
from webapp.admin.usuarios import router_usuarios
from webapp.auth import router_login
from webapp.crear_carnet import router_crear_carnet
from webapp.home import router_home
from webapp.resultado_busqueda import router_resultado_busqueda
from webapp.crear_carnet.carnets import router_carnet_solicitados
from webapp.crear_carnet.carnets import router_carnet_hechos
from webapp.crear_carnet.carnets import router_carnet_entregados
from webapp.crear_carnet.carnets import router_carnet_eliminados
from webapp.crear_carnet.carnets import router_carnet_con_errores
from webapp.crear_carnet.carnets import router_carnet_administrar
from webapp.folio import router_folio
from webapp.error import error
from webapp.soporte.about import router_about
from webapp.soporte.contact import router_contact
from webapp.visitante import router_categoria
from webapp.visitante import router_estado
from webapp.visitante import router_control_visitante
from webapp.visitante import router_home_visitante
from webapp.crear_carnet.carnets import router_crear_matriculados
from webapp.crear_carnet import  router_crear_matriculado
from api.endpoints import router_imprimir_carnet
from webapp.admin.registro import router_registro

api_router = APIRouter()

api_router.include_router(router_home.router, prefix="", tags=["Inicio"])
api_router.include_router(router_login.router, prefix="", tags=["Iniciar Sesión"])
api_router.include_router(router_admin.router, prefix="", tags=["Administración"])
api_router.include_router(
    router_motivos_admin.router, prefix="", tags=["Tipos de Motivos"]
)
api_router.include_router(
    router_motivos_crear.router, prefix="", tags=["Crear Tipos de Motivos"]
)
api_router.include_router(router_crear_carnet.router, prefix="", tags=["Crear Carnet"])
api_router.include_router(
    router_edit_tipo_motivo.router, prefix="", tags=["Editar Carnet"]
)
api_router.include_router(router_usuarios.router, prefix="", tags=["Usuarios"])
api_router.include_router(
    router_form_usuarios.router, prefix="", tags=["Formulario de Usuarios"]
)
api_router.include_router(
    router_resultado_busqueda.router, prefix="", tags=["Resultado de Busqueda"]
)
api_router.include_router(
    router_edit_usuario.router, prefix="", tags=["Editar usuario"]
)
api_router.include_router(
    router_carnet_solicitados.router, prefix="", tags=["Carnets solicitados"]
)
api_router.include_router(
    error.router, prefix= "", tags=["error"]
)

api_router.include_router(
    router_carnet_hechos.router, prefix="", tags=["Carnets hechos"]
)
api_router.include_router(
    router_carnet_entregados.router, prefix="", tags=["Carnets entregados"]
)
api_router.include_router(
    router_carnet_eliminados.router, prefix="", tags=["Carnets Eliminados"]
)
api_router.include_router(
    router_carnet_con_errores.router, prefix="", tags=["Carnets con Errores"]
)
api_router.include_router(
    router_carnet_administrar.router, prefix="", tags=["Carnets Administrar"]
)
api_router.include_router(
    router_crear_matriculados.router, prefix="", tags=["Crear carnets por lotes para matriculados"]
)
api_router.include_router(
    router_crear_matriculado.router, prefix="", tags=["Crear carnets para un matriculado"]
)

api_router.include_router(
    router_imprimir_carnet.router, prefix="", tags=["imprimir_carnet_activo"]
)

api_router.include_router(
    router_folio.router, prefix="", tags=["Regisro de Folios"]
)

api_router.include_router(
    router_registro.router, prefix="", tags=["Regisro de acciones de usuarios"]
)

api_router.include_router(router_about.router, prefix="", tags=["Acerca de"])
api_router.include_router(router_contact.router, prefix="", tags=["Contacto"])
api_router.include_router(router_categoria.router, prefix="", tags=["Categoria"])
api_router.include_router(router_estado.router, prefix="", tags=["Estado"])
api_router.include_router(router_control_visitante.router, prefix="", tags=["Visitante"])
api_router.include_router(router_home_visitante.router, prefix="", tags=["Home"])
