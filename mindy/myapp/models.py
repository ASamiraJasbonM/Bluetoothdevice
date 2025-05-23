from django.db import models

# Create your models here.
from django.contrib.auth.hashers import make_password, check_password




class IdeaIrracional(models.Model):
    categoria = models.CharField(max_length=100)
    tipo = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.tipo} - {self.categoria}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class TipoIdea(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='tipos')
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"


# Cada uno de estos modelos representa una lista de opciones asociadas a un Tipo de idea irracional

class Provoca(models.Model):
    tipo = models.ForeignKey(TipoIdea, on_delete=models.CASCADE, related_name='provoca')
    texto = models.TextField()

    def __str__(self):
        return self.texto

class PruebaAFavor(models.Model):
    tipo = models.ForeignKey(TipoIdea, on_delete=models.CASCADE, related_name='pruebas_a_favor')
    texto = models.TextField()

    def __str__(self):
        return self.texto

class PruebaEnContra(models.Model):
    tipo = models.ForeignKey(TipoIdea, on_delete=models.CASCADE, related_name='pruebas_en_contra')
    texto = models.TextField()

    def __str__(self):
        return self.texto

class Utilidad(models.Model):
    tipo = models.ForeignKey(TipoIdea, on_delete=models.CASCADE, related_name='utilidades')
    texto = models.TextField()

    def __str__(self):
        return self.texto

class IdeaRealista(models.Model):
    tipo = models.ForeignKey(TipoIdea, on_delete=models.CASCADE, related_name='ideas_realistas')
    texto = models.TextField()

    def __str__(self):
        return self.texto


class ReferenciaCIE10(models.Model):
    tabla = models.CharField(max_length=50)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Usuarios(models.Model):
    cedula = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    contraseña = models.CharField(max_length=100, blank=True, null=True)
    fechanacimiento = models.CharField(max_length=100, blank=True, null=True)
    tipoa = models.CharField(
        max_length=20,
        choices=[
            ("Participante", "Participante"),
            ("Profesional", "Profesional"),
            ("Administrador", "Administrador"),
            ("Investigador", "Investigador"),
        ]
    )
    direccion = models.CharField(max_length=100, blank=True, null=True)
    spreguntas = models.CharField(max_length=20,
        choices=[
            ("0", "¿Cuál fue su primer colegio?"),
            ("1", "¿Nombre de su primera mascota?"),
            ("2", "¿Nombre de su pariente más cercano?"),
            ("3", "¿Año de expedición de la cedula?"),
            ("4", "¿Cuál es su flor favorita?"),
        ])
    preguntas = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipoa})"

    def set_password(self, password):
        """Encriptamos la contraseña antes de guardarla."""
        self.contraseña = make_password(password)

    def check_password(self, password):
        """Verificamos la contraseña encriptada."""
        return check_password(password, self.contraseña)
    
est=[
["0", "Soltero"],
["1", "Casado"],
["2", "Divorciado"],
["3", "union libre"],
["4", "viudo"],
]

sx=[
["0", "Mujer"],
["1", "Hombre"],
]

class Encuesta(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
class Usuariosparticipantes(models.Model):
    cedula = models.CharField(max_length=100, unique=True)
    correo1 = models.CharField(max_length=100, blank=True, null=True)
    correo2 = models.CharField(max_length=100, blank=True, null=True)
    estciv = models.CharField(max_length=100, choices=est)
    sexo = models.CharField(max_length=100, choices=sx)
    contactoE1 = models.CharField(max_length=255, default='N/A')
    NumConE1 = models.CharField(max_length=100, null=True, blank=True)
    citas_asistidas = models.FloatField(blank=True, null=True)
    citas_inasistidas = models.FloatField(blank=True, null=True)
    recuperacion = models.IntegerField(default=0)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True)
    Nencuestashechas = models.FloatField(blank=True, null=True, default=0)
    encuestas_hechas = models.ManyToManyField(Encuesta, related_name='realizadas_por', blank=True)
    encuestas_pendientes = models.ManyToManyField(Encuesta, related_name='pendientes_para', blank=True)

    def __str__(self):
        return f"{self.cedula} (Participante)"


class Cita(models.Model):
    cedula = models.CharField(max_length=20)  # puede incluir letras si usas pasaportes
    dia = models.DateField()
    hora = models.TimeField()
    profesional = models.CharField(max_length=100)
    asistida = models.BooleanField(default=False)   # Para marcar si la cita fue asistida o no

    def __str__(self):
        return f"Cita de {self.cedula} con {self.profesional} el {self.dia} a las {self.hora}"

class Drogas(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # sin choices

    def __str__(self):
        return self.nombre

class historialmed(models.Model):
    paciente = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    iniciotrat = models.DateField(blank=True, null=True)
    ultimocon = models.DateField(blank=True, null=True)
    recaidas = models.FloatField(blank=True, null=True)
    diagnostico = models.CharField(max_length=100)
    consumo = models.ManyToManyField(Drogas, related_name="historiales")
    profesional = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Historial de {self.paciente.cedula} con {self.profesional}"

class Educativo(models.Model):
    numero = models.PositiveIntegerField(unique=True, blank=True, null=True)
    tipsdia = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(blank=True, null=True)  # campo para links
    mensajeprevent = models.CharField(max_length=255)
    mensajetexto = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='educativos/', blank=True, null=True)  
    def __str__(self):
        return self.tipsdia

TIPO_PREGUNTA_CHOICES = [
    ('OMM', 'Opción múltiple con múltiples respuestas'),
    ('OMU', 'Opción múltiple con única respuesta'),
    ('OMMC', 'Opción múltiple con múltiples respuestas columna'),
    ('OMUC', 'Opción múltiple con única respuesta columna'),
    ('OMMV', 'Opción múltiple con múltiples respuestas vertical'),
    ('OMUV', 'Opción múltiple con única respuesta Vertical'),
    ('AB', 'Pregunta abierta'),
    ('VF', 'Verdadero o falso'),
    ('PRP', 'Pregunta relacion proporcionales')
]

class PreguntaEncuesta(models.Model):
    numero_encuesta = models.IntegerField()
    numero_pregunta = models.PositiveSmallIntegerField()  # dos dígitos como máximo
    pregunta = models.TextField()
    tipo_pregunta = models.CharField(max_length=8, choices=TIPO_PREGUNTA_CHOICES)
    puntaje_pregunta = models.FloatField()
    numero_opciones_respuesta = models.PositiveSmallIntegerField(default=0)

    posible_respuesta_1 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_1 = models.FloatField(blank=True, null=True)

    posible_respuesta_2 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_2 = models.FloatField(blank=True, null=True)

    posible_respuesta_3 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_3 = models.FloatField(blank=True, null=True)

    posible_respuesta_4 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_4 = models.FloatField(blank=True, null=True)

    posible_respuesta_5 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_5 = models.FloatField(blank=True, null=True)

    posible_respuesta_6 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_6 = models.FloatField(blank=True, null=True)

    posible_respuesta_7 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_7 = models.FloatField(blank=True, null=True)

    posible_respuesta_8 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_8 = models.FloatField(blank=True, null=True)

    posible_respuesta_9 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_9 = models.FloatField(blank=True, null=True)

    posible_respuesta_10 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_10 = models.FloatField(blank=True, null=True)

    posible_respuesta_11 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_11 = models.FloatField(blank=True, null=True)

    posible_respuesta_12 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_12 = models.FloatField(blank=True, null=True)

    posible_respuesta_13 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_13 = models.FloatField(blank=True, null=True)

    posible_respuesta_14 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_14 = models.FloatField(blank=True, null=True)

    posible_respuesta_15 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_15 = models.FloatField(blank=True, null=True)

    posible_respuesta_16 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_16 = models.FloatField(blank=True, null=True)

    posible_respuesta_17 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_17 = models.FloatField(blank=True, null=True)

    posible_respuesta_18 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_18 = models.FloatField(blank=True, null=True)

    posible_respuesta_19 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_19 = models.FloatField(blank=True, null=True)

    posible_respuesta_20 = models.CharField(max_length=255, blank=True, null=True)
    valor_respuesta_20 = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('numero_encuesta', 'numero_pregunta')  # evita preguntas duplicadas en una misma encuesta

    def __str__(self):
        return f"Encuesta {self.numero_encuesta} - Pregunta {self.numero_pregunta}"
    
class EncuestaRespondida(models.Model):
    numero_encuesta = models.IntegerField()
    cedula_usuario = models.CharField(max_length=20)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encuesta {self.numero_encuesta} - Usuario {self.cedula_usuario}"
    

class foro(models.Model):
    usuario = models.IntegerField()
    tema = models.CharField(max_length=20)
    fechapub = models.DateTimeField(auto_now_add=True)
    fechaact = models.DateTimeField(auto_now_add=True)
    tema = models.CharField(max_length=20)
    
    
    def __str__(self):
        return self.tema
    
class temaforo(models.Model):
    usuario = models.IntegerField()
    tema = models.CharField(max_length=20)
    fechapub = models.DateTimeField(auto_now_add=True)
    fechaact = models.DateTimeField(auto_now_add=True)
    tema = models.CharField(max_length=20)
    
    
    def __str__(self):
        return self.tema



class RespuestaUsuario(models.Model):
    encuesta_respondida = models.ForeignKey(EncuestaRespondida, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(PreguntaEncuesta, on_delete=models.CASCADE)
    
    respuesta = models.TextField()  # Puede guardar texto, lista codificada (JSON), etc.
    puntaje_obtenido = models.FloatField(null=True, blank=True)  # Si aplica

    def __str__(self):
        return f"Usuario {self.encuesta_respondida.cedula_usuario} - Pregunta {self.pregunta.numero_pregunta}"
    


class EIdeaIrracional(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True)
    categoria = models.CharField(max_length=100)
    tipo = models.CharField(max_length=200)
    provoca = models.TextField()
    pruebas_a_favor = models.TextField()
    pruebas_en_contra = models.TextField()
    utilidad = models.TextField()
    idea_realista = models.TextField()

    def __str__(self):
        return f"{self.tipo} - {self.categoria}"
    

from django.utils import timezone

class RegistroSensor(models.Model):
    usuario_id = models.CharField(max_length=50)
    hora = models.DateTimeField(default=timezone.now)
    humedad = models.FloatField()
    temperatura_ambiente = models.FloatField()
    temperatura_corporal = models.FloatField()
    avg_bpm = models.FloatField()

    def __str__(self):
        return f"{self.usuario_id} - {self.hora}"

class DatoSensor(models.Model):
    device = models.CharField(max_length=50, default=None)
    #userId = models.CharField(max_length=64, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    temperatura_corporal = models.FloatField()
    temperatura_ambiental = models.FloatField()
    bpm = models.IntegerField()
    avg_bpm = models.IntegerField()
    humedad = models.FloatField()
    estado = models.CharField(max_length=50, default="Conectando")


class ConnectionSensor(models.Model):
    device = models.CharField(max_length=50, default=None)
    userId = models.CharField(max_length=64, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    temperatura_corporal = models.FloatField()
    temperatura_ambiental = models.FloatField()
    bpm = models.IntegerField()
    avg_bpm = models.IntegerField()
    humedad = models.FloatField()
    estado = models.CharField(max_length=50, default="Conectando")