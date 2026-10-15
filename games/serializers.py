from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Juego, Resena

User = get_user_model()


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirmacion = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirmacion")
        read_only_fields = ("id",)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmacion"]:
            raise serializers.ValidationError(
                {"password_confirmacion": "Las contraseñas no coinciden."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirmacion")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class JuegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Juego
        fields = (
            "id", "titulo", "descripcion", "plataforma", "anio_lanzamiento"
        )


class ResenaSerializer(serializers.ModelSerializer):
    usuario = UsuarioPublicoSerializer(read_only=True)
    usuario_id = serializers.IntegerField(source="usuario.id", read_only=True)
    juego_titulo = serializers.CharField(source="juego.titulo", read_only=True)

    class Meta:
        model = Resena
        fields = (
            "id", "usuario", "usuario_id", "juego", "juego_titulo",
            "contenido", "fecha_creacion", "fecha_actualizacion", "calificacion"
        )
        read_only_fields = (
            "id", "usuario", "usuario_id", "juego_titulo",
            "fecha_creacion", "fecha_actualizacion"
        )

    def validate_calificacion(self, value):
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5.")
        return value
