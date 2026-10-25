from django.urls import path

from rest_framework.routers import DefaultRouter
from .views import  detalle_juego,crear_resena, iniciar_sesion, cerrar_sesion, registrarse

router = DefaultRouter()
#router.register("juegos", JuegoViewSet, basename="juego")
#router.register("resenas", ResenaViewSet, basename="resena")

urlpatterns = router.urls

urlpatterns = [
    path(
        "juegos/<int:juego_id>/",
        detalle_juego,
        name="detalle_juego",
    ),
    path(
        "juegos/<int:juego_id>/resenas/nueva/",
        crear_resena,
        name="crear_resena",
    ), 
    path("login/", iniciar_sesion, name="iniciar_sesion"),
    path("logout/", cerrar_sesion, name="cerrar_sesion"),
    path("registro/", registrarse, name="registrarse"),
]