from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Juego(models.Model):
    class Plataforma(models.TextChoices):
        PC = "PC", "PC"
        PLAYSTATION = "PlayStation", "PlayStation"
        NINTENDO = "Nintendo", "Nintendo"
        XBOX = "Xbox", "Xbox"

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    plataforma = models.CharField(max_length=20, choices=Plataforma.choices)
    anio_lanzamiento = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo


class Resena(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    juego = models.ForeignKey(
        Juego,
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    # Bono opcional del proyecto: puntuación de 1 a 5 estrellas.
    calificacion = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    class Meta:
        ordering = ["-fecha_creacion"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "juego"],
                name="una_resena_por_usuario_juego"
            ),
            models.CheckConstraint(
                condition=models.Q(calificacion__isnull=True)
                | models.Q(calificacion__gte=1, calificacion__lte=5),
                name="calificacion_entre_1_y_5",
            )
        ]

    def __str__(self):
        return f"Reseña de {self.usuario} sobre {self.juego}"
