from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Juego, Resena
from .permissions import EsAdministradorOConsulta, EsAutorOConsulta
from .serializers import RegistroSerializer, JuegoSerializer, ResenaSerializer
from django.shortcuts import render, get_object_or_404
from .models import Juego, Resena
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ResenaForm

User = get_user_model()


class RegistroAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise ValidationError({"refresh": "Debes enviar el refresh token."})
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            raise ValidationError({"refresh": "El refresh token no es válido."})
        return Response({"detail": "Sesión cerrada correctamente."})


class JuegoViewSet(viewsets.ModelViewSet):
    queryset = Juego.objects.all()
    serializer_class = JuegoSerializer
    permission_classes = [EsAdministradorOConsulta]


class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.select_related("usuario", "juego").all()
    serializer_class = ResenaSerializer
    permission_classes = [IsAuthenticated, EsAutorOConsulta]

    def get_queryset(self):
        queryset = super().get_queryset()
        juego_id = self.request.query_params.get("juego")
        if juego_id:
            queryset = queryset.filter(juego_id=juego_id)
        # ?mias=true devuelve las reseñas del usuario autenticado.
        if self.request.query_params.get("mias", "").lower() == "true":
            queryset = queryset.filter(usuario=self.request.user)
        return queryset

    def perform_create(self, serializer):
        # El usuario se toma del token; el cliente no puede suplantar al autor.
        serializer.save(usuario=self.request.user)





def detalle_juego(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)

    resenas = (
        Resena.objects
        .filter(juego=juego)
        .select_related("usuario")
        .order_by("-fecha_creacion")
    )

    return render(
        request,
        "detalle_juego.html",
        {
            "juego": juego,
            "resenas": resenas,
        },
    )


#@login_required
def crear_resena(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)

    if request.method == "POST":
        form = ResenaForm(request.POST)

        if form.is_valid():
            resena = form.save(commit=False)
            resena.usuario = request.user
            resena.juego = juego
            resena.save()

            return redirect(
                "detalle_juego",
                juego_id=juego.id,
            )
    else:
        form = ResenaForm()

    return render(
        request,
        "crear_resena.html",
        {
            "juego": juego,
            "form": form,
        },
    )

