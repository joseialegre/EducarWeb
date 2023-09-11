from django.db import models
from django.utils import timezone
from apps.usuario.models import Usuario
from django.conf import settings

# Create your models here.


# Categoria
class Categoria(models.Model):
    nombre = models.CharField(max_length=30, null=False,unique=True)

    class Meta:
        ordering = ('-nombre',)

    def __str__(self):
        return self.nombre


class Post(models.Model):
    titulo = models.CharField(max_length=50, null=False)
    subtitulo = models.CharField(max_length=100, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    texto = models.TextField(null=False)
    activo = models.BooleanField(default=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, default='Sin Categoria')
    imagen = models.ImageField(
        null=True, blank=True, upload_to='media/', default='static/post_default.png')
    publicado = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, default=1)


    class Meta:
        ordering = ['-publicado']

    def __str__(self):
        return self.titulo

    def puede_editar(self, user):
        return user.es_colaborador and user == self.usuario

    def puede_eliminar(self, user):
        return user.es_colaborador and user == self.usuario

    def delete(self, using=None, keep_parents=False):
        print(self.imagen.name)
        if self.imagen.name != 'static/post_default.png':
            self.imagen.delete(self.imagen.name)
        super().delete()


class Comentario(models.Model):
    posts = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def puede_editar(self, user):
        return  user == self.usuario

    def puede_eliminar(self, user):
        return (user == self.usuario) or (self.posts.usuario == user)

    def __str__(self):
        return self.texto