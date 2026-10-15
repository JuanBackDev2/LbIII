from django.contrib import messages
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



def detalle_juego(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)

    resenas = (
        Resena.objects
        .filter(juego=juego)
        .select_related("usuario")
        .order_by("-fecha_creacion")
    )

    ya_reseno = (
        request.user.is_authenticated
        and Resena.objects.filter(
            usuario=request.user,
            juego=juego
        ).exists()
    )

    return render(
        request,
        "detalle_juego.html",
        {
            "juego": juego,
            "resenas": resenas,
            "ya_reseno": ya_reseno,
        },
    )


#@login_required
def crear_resena(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)

    if Resena.objects.filter(
        usuario=request.user,
        juego=juego
    ).exists():
        messages.error(request, "Ya has publicado una reseña para este juego.")
        return redirect("detalle_juego", juego_id=juego.id)

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

