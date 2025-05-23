from django.contrib import admin
from .models import Usuarios, Usuariosparticipantes, Educativo, PreguntaEncuesta, historialmed, Cita, RespuestaUsuario, EncuestaRespondida, temaforo, Drogas, ReferenciaCIE10
from .models import Provoca, PruebaAFavor, PruebaEnContra, Utilidad, IdeaRealista, DatoSensor, RegistroSensor

class participanteAdmin(admin.ModelAdmin):
    list_display=["cedula","tipoa"]

# Register your models here.
admin.site.register(RegistroSensor)
admin.site.register(Provoca)
admin.site.register(DatoSensor)

admin.site.register(Utilidad)
admin.site.register(PruebaAFavor)
admin.site.register(PruebaEnContra)
admin.site.register(IdeaRealista)


admin.site.register(Usuarios)
admin.site.register(Usuariosparticipantes)
admin.site.register(Educativo)
admin.site.register(PreguntaEncuesta)
admin.site.register(historialmed)
admin.site.register(Cita)
admin.site.register(RespuestaUsuario)
admin.site.register(EncuestaRespondida)
admin.site.register(temaforo)
admin.site.register(Drogas)
admin.site.register(ReferenciaCIE10)


