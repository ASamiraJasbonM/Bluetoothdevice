from django import forms
#from .models import Pregunta, Respuesta
# myapp/forms.py
from django import forms
from .models import Usuarios, Usuariosparticipantes, Drogas, historialmed, Educativo



class ExcelUploadForm(forms.Form):
    archivo = forms.FileField(label='Selecciona el archivo Excel')

class CedulaSearchForm(forms.Form):
    cedula = forms.CharField(max_length=20, required=True, label="Cédula")

class EducativoForm(forms.ModelForm):
    class Meta:
        model = Educativo
        fields = ['numero', 'tipsdia', 'link', 'mensajeprevent', 'mensajetexto', 'imagen']


class DrogasForm(forms.ModelForm):
    class Meta:
        model = Drogas
        fields = ['nombre']

class HistorialmedForm(forms.ModelForm):
    iniciotrat = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="¿Cuando fue el inicio del tratamiento?"
    )
    ultimocon = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="¿Cuando fue el último control?"
    )

    class Meta:
        model = historialmed
        fields = ["iniciotrat", "ultimocon", "recaidas", "diagnostico", "consumo"]
        labels = {
            "iniciotrat": "Inicio del tratamiento",
            "ultimocon": "Último control",
            "recaidas": "¿Ha tenido recaídas?",
            "diagnostico": "Diagnóstico médico",
            "consumo": "Consumo actual",
        }

class newpatient(forms.ModelForm):
    class Meta:
        model = Usuariosparticipantes
        fields = ["cedula", "estciv", "sexo", "citas_asistidas", "citas_inasistidas"]
        labels = {
            "cedula": "Número de cédula",
            "estciv": "Estado civil",
            "sexo": "Sexo",
            "citas_asistidas": "Citas asistidas",
            "citas_inasistidas": "Citas inasistidas",
        }

class CambiarContraseñaForm(forms.Form):
    contraseña_actual = forms.CharField(widget=forms.PasswordInput, label="Contraseña actual")
    nueva_contraseña = forms.CharField(widget=forms.PasswordInput, label="Nueva contraseña")
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput, label="Confirmar nueva contraseña")


'''class CrearCuentaForm(forms.Form):
    cedula = forms.CharField(max_length=20, label="Cédula")
    nombre = forms.CharField(max_length=100, label="Nombres")
    apellidos = forms.CharField(max_length=100, label="Apellidos")
    correo1 = forms.EmailField(label="Correo")
    correo2 = forms.EmailField(label="Confirmar correo")
    fechanacimiento = forms.DateField(label="Fecha de nacimiento", widget=forms.DateInput(attrs={'type': 'date'}))
    direccion = forms.CharField(max_length=255, label="Dirección")
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    validar_contraseña = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)
    aceptar_politica = forms.BooleanField(
        label="He leído y acepto la política de privacidad y tratamiento de datos",
        required=True
    )
    spreguntas=forms.CharField()
    preguntas=forms.CharField(label="pregunta de seguridad")
    def clean(self):
        cleaned_data = super().clean()
        
        if cleaned_data.get("correo1") != cleaned_data.get("correo2"):
            raise forms.ValidationError("Los correos no coinciden.")
        
        if cleaned_data.get("contraseña") != cleaned_data.get("validar_contraseña"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data'''

class CrearCuentaForm(forms.Form):
    cedula = forms.CharField(max_length=20)
    nombre = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)
    correo1 = forms.EmailField(label='Correo')
    correo2 = forms.EmailField(label='Confirmar correo')
    contraseña = forms.CharField(widget=forms.PasswordInput)
    validar_contraseña = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')
    fechanacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    direccion = forms.CharField(max_length=255)
    aceptar_politica = forms.BooleanField(required=True)
    spreguntas = forms.CharField(required=True)
    preguntas = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        correo1 = cleaned_data.get('correo1')
        correo2 = cleaned_data.get('correo2')
        contraseña = cleaned_data.get('contraseña')
        validar_contraseña = cleaned_data.get('validar_contraseña')

        if correo1 and correo2 and correo1 != correo2:
            self.add_error('correo2', 'Los correos no coinciden.')

        if contraseña and validar_contraseña and contraseña != validar_contraseña:
            self.add_error('validar_contraseña', 'Las contraseñas no coinciden.')

class RegistroPorCedulaForm(forms.Form):
    cedula = forms.CharField(label="Cédula registrada", max_length=100)
    correo = forms.EmailField(label="Correo electrónico")
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        cedula = cleaned_data.get("cedula")
        correo = cleaned_data.get("correo")

        try:
            usuario = Usuarios.objects.get(cedula=cedula)
        except Usuarios.DoesNotExist:
            raise forms.ValidationError("La cédula no está registrada. Contacta a un administrador.")

        if usuario.contraseña and usuario.correo:
            raise forms.ValidationError("Ya existe una cuenta con esta cédula.")

        if Usuarios.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        
        return cleaned_data


from django import forms
from .models import (
    IdeaIrracional, Provoca, PruebaAFavor,
    PruebaEnContra, Utilidad, IdeaRealista
)

class IdeaFormulario(forms.Form):
    idea = forms.ModelChoiceField(queryset=IdeaIrracional.objects.all(), label="Tipo de idea irracional")

    provoca = forms.ModelMultipleChoiceField(
        queryset=Provoca.objects.none(),  # se actualizará con JavaScript según la idea
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="¿Qué provoca en mí esa idea?"
    )
    otra_provoca = forms.CharField(required=False, label="Otra opción (provoca)")

    pruebas_a_favor = forms.ModelMultipleChoiceField(
        queryset=PruebaAFavor.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Pruebas a favor"
    )
    otra_prueba_a_favor = forms.CharField(required=False, label="Otra opción (a favor)")

    pruebas_en_contra = forms.ModelMultipleChoiceField(
        queryset=PruebaEnContra.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Pruebas en contra"
    )
    otra_prueba_en_contra = forms.CharField(required=False, label="Otra opción (en contra)")

    utilidad = forms.ModelMultipleChoiceField(
        queryset=Utilidad.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="¿Es útil pensarlo así?"
    )
    otra_utilidad = forms.CharField(required=False, label="Otra opción (utilidad)")

    idea_realista = forms.ModelChoiceField(
        queryset=IdeaRealista.objects.none(),
        required=False,
        label="Idea realista"
    )
    otra_idea_realista = forms.CharField(required=False, label="Otra idea realista")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si ya se seleccionó una idea, actualizamos los queryset
        if 'idea' in self.data:
            try:
                idea_id = int(self.data.get('idea'))
                self.fields['provoca'].queryset = Provoca.objects.filter(idea_id=idea_id)
                self.fields['pruebas_a_favor'].queryset = PruebaAFavor.objects.filter(idea_id=idea_id)
                self.fields['pruebas_en_contra'].queryset = PruebaEnContra.objects.filter(idea_id=idea_id)
                self.fields['utilidad'].queryset = Utilidad.objects.filter(idea_id=idea_id)
                self.fields['idea_realista'].queryset = IdeaRealista.objects.filter(idea_id=idea_id)
            except (ValueError, TypeError):
                pass  # en caso de error, dejar queryset vacío
from .models import (
    Categoria, TipoIdea,
    Provoca, PruebaAFavor, PruebaEnContra, Utilidad, IdeaRealista
)

class OpcionIdeasForm(forms.Form):
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), label="Categoría")
    tipo_idea = forms.ModelChoiceField(queryset=TipoIdea.objects.all(), label="Tipo de Idea")

    provoca = forms.CharField(required=False, widget=forms.Textarea, label="¿Qué provoca en mí esa idea?")
    prueba_a_favor = forms.CharField(required=False, widget=forms.Textarea, label="Prueba a favor")
    prueba_en_contra = forms.CharField(required=False, widget=forms.Textarea, label="Prueba en contra")
    utilidad = forms.CharField(required=False, widget=forms.Textarea, label="¿Es útil pensarlo así?")
    idea_realista = forms.CharField(required=False, widget=forms.Textarea, label="Idea realista")



# class PreguntaForm(forms.ModelForm):
#     class Meta:
#         model = Pregunta
#         fields = ['titulo', 'descripcion']

# class RespuestaForm(forms.ModelForm):
#     class Meta:
#         model = Respuesta
#         fields = ['pregunta', 'contenido']