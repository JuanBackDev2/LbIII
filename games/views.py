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
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
User = get_user_model()
from django.views.decorators.http import require_POST
from django.db.models import Avg

"""
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
"""

def registrarse(request):
    if request.user.is_authenticated:
        return redirect("detalle_juego", juego_id=1)

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        acepta_terminos = request.POST.get("terms") == "on"

        errores = []

        if not email:
            errores.append("El correo electrónico es obligatorio.")

        if not username:
            errores.append("El nombre de usuario es obligatorio.")

        if User.objects.filter(username__iexact=username).exists():
            errores.append("Ese nombre de usuario ya está registrado.")

        if email and User.objects.filter(email__iexact=email).exists():
            errores.append("Ese correo electrónico ya está registrado.")

        if not acepta_terminos:
            errores.append("Debes aceptar los términos para crear tu cuenta.")

        try:
            validate_password(password)
        except ValidationError as e:
            errores.extend(e.messages)

        if errores:
            for error in errores:
                messages.error(request, error)

            return render(request, "registro.html")

        try:
            with transaction.atomic():
                usuario = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )

            login(request, usuario)
            messages.success(request, "¡Tu cuenta se creó correctamente!")
            return redirect("detalle_juego", juego_id=1)

        except IntegrityError:
            messages.error(
                request,
                "No se pudo crear la cuenta. "
                "Comprueba si el usuario o correo ya existe."
            )

    return render(request, "registro.html")

def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("detalle_juego", juego_id=1)  # Ajusta al nombre de tu ruta del catálogo

    if request.method == "POST":
        identificador = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")

        # Permite ingresar con nombre de usuario o correo electrónico
        usuario = User.objects.filter(email__iexact=identificador).first()
        username = usuario.username if usuario else identificador

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)  # Crea la sesión autenticada
            destino = request.GET.get("next")

            if destino and destino.startswith("/") and not destino.startswith("//"):
                return redirect(destino)

            return redirect("detalle_juego", juego_id=1)

        messages.error(request, "Usuario/correo o contraseña incorrectos.")

    return render(request, "login.html")


@require_POST
def cerrar_sesion(request):
    logout(request)  # Cierra la sesión
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("iniciar_sesion")

@login_required
def detalle_juego(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)

    resenas = (
        Resena.objects
        .filter(juego=juego)
        .select_related("usuario")
        .order_by("-fecha_creacion")
    )

    ya_reseno = False
    mi_resena = None

    if request.user.is_authenticated:
        mi_resena = Resena.objects.filter(
            usuario=request.user,
            juego=juego
        ).first()

        ya_reseno = mi_resena is not None

    promedio = Resena.objects.filter(
    juego=juego,
    calificacion__isnull=False
    ).aggregate(promedio=Avg("calificacion"))["promedio"]

    porcentaje_jugabilidad = (
    (promedio / 5) * 100
    if promedio is not None
    else 0
)

    return render(
        request,
        "detalle_juego.html",
        {
            "juego": juego,
            "resenas": resenas,
            "ya_reseno": ya_reseno,
            "mi_resena": mi_resena,
            "promedio": promedio,
            "porcentaje_jugabilidad": porcentaje_jugabilidad,
        },
    )


@login_required
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

def catalogo(request):
    juegos = Juego.objects.all().order_by("titulo")

    return render(
        request,
        "catalogo.html",
        {
            "juegos": juegos,
        }
    )

@login_required
def editar_resena(request, resena_id):

    resena = get_object_or_404(
        Resena,
        id=resena_id,
        usuario=request.user
    )

    if request.method == "POST":
        form = ResenaForm(
            request.POST,
            instance=resena
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Tu reseña se actualizó correctamente."
            )

            return redirect(
                "detalle_juego",
                juego_id=resena.juego.id
            )

    else:
        form = ResenaForm(instance=resena)

    return render(request, "crear_resena.html", {
        "form": form,
        "juego": resena.juego,
        "resena": resena,
        "modo_edicion": True
    })

@login_required
def eliminar_resena(request, resena_id):

    resena = get_object_or_404(
        Resena,
        id=resena_id,
        usuario=request.user
    )

    juego_id = resena.juego.id

    if request.method == "POST":
        resena.delete()

        messages.success(
            request,
            "Tu reseña se eliminó correctamente."
        )

        return redirect(
            "detalle_juego",
            juego_id=juego_id
        )

    return redirect(
        "detalle_juego",
        juego_id=juego_id
    )

@login_required
def mis_resenas(request):
    resenas = (
        Resena.objects
        .filter(usuario=request.user)
        .select_related("juego")
        .order_by("-fecha_creacion")
    )

    total_resenas = resenas.count()

    return render(request, "mis_resenas.html", {
        "resenas": resenas,
        "total_resenas": total_resenas,
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import JuegoForm
from .models import Juego


@staff_member_required
def agregar_juego(request):

    if request.method == "POST":
        form = JuegoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "El videojuego se agregó correctamente.")
            return redirect("agregar_juego")

    else:
        form = JuegoForm()

    juegos = Juego.objects.all().order_by("-id")

    return render(request, "paneladmin.html", {
        "form": form,
        "juegos": juegos,
    })