
from django import forms
from .models import Juego, Resena


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ["calificacion", "contenido"]
        widgets = {
            "calificacion": forms.NumberInput(
                attrs={
                    "type": "range",
                    "id": "scoreRange",
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "class": (
                        "w-full accent-primary-container "
                        "bg-surface-container-high rounded-full "
                        "cursor-pointer h-2"
                    ),
                }
            ),
            "contenido": forms.Textarea(
                attrs={
                    "id": "reviewContent",
                    "maxlength": 2500,
                    "rows": 6,
                    "placeholder": (
                        "Escribe aquí tu análisis del videojuego..."
                    ),
                    "class": (
                        "w-full bg-surface-container-low rounded-xl "
                        "border border-outline-variant/50 p-4 "
                        "text-body-md text-on-surface "
                        "focus:outline-none focus:border-primary "
                        "focus:ring-1 focus:ring-primary "
                        "transition-all leading-relaxed resize-y"
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["calificacion"].required = False
        self.fields["contenido"].required = True
        
        if self.instance and self.instance.pk:
            self.fields["calificacion"].initial = self.instance.calificacion
        else:
            self.fields["calificacion"].initial = 3
        


class JuegoForm(forms.ModelForm):
    class Meta:
        model = Juego
        fields = [
            "titulo",
            "descripcion",
            "plataforma",
            "anio_lanzamiento",
            "caratula",
        ]

        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "w-full bg-surface-container-low border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface",
                "placeholder": "Nombre del videojuego",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "w-full bg-surface-container-low border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface",
                "rows": 4,
            }),
            "plataforma": forms.Select(attrs={
                "class": "w-full md:w-80 bg-surface-container-low border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface",
            }),
            "anio_lanzamiento": forms.NumberInput(attrs={
                "class": "w-full md:w-48 bg-surface-container-low border border-outline-variant rounded-lg px-4 py-2.5 text-on-surface",
            }),
            "caratula": forms.ClearableFileInput(attrs={
                "class": "text-on-surface",
                "accept": "image/*",
            }),
        }
