
from django import forms
from .models import Resena


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
        self.fields["calificacion"].initial = 3
        self.fields["contenido"].required = True






