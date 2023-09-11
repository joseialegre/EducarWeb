from django.shortcuts import render ,redirect
from .forms import RegistroUsuarioform
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView,DeleteView,ListView
from django.contrib import messages
from django.urls import reverse,reverse_lazy
from django.contrib.auth import login
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.posts.models import Post,Comentario , Usuario
from django.contrib.auth.decorators import login_required

# Create your views here.


class RegistrarUsuario(CreateView):
    template_name = 'register/register.html'
    form_class = RegistroUsuarioform

    def form_valid(self, form):
        messages.success(
            self.request, 'Registro exitoso. Por favor inicia sesión.')
        form.save()
        next_url = self.request.GET.get('next')
        if next_url:
            self.request.session['next'] = next_url

        return redirect('apps.usuario:login')


class LoginUsuario(LoginView):
    template_name = 'register/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = self.request.GET.get('next')
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            messages.success(self.request, 'Inicio de sesión exitoso.')
            login(self.request, form.get_user())  # Autenticar al usuario
            next_url = self.request.GET.get('next') or reverse('apps.posts:index')
            return JsonResponse({'success': True, 'next_url': next_url})
        else:
            return JsonResponse({'success': False, 'message': 'Usuario o contraseña incorrectos.'})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'message': 'Usuario o contraseña incorrectos.'})

class LogoutUsuario(LogoutView):
    template_name = 'registration/logout.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'Logout exitoso')
        return redirect('apps.usuario:login')

    def get_next_page(self):
        return reverse('apps.usuario:login')

class UsuarioListView(LoginRequiredMixin,ListView):
    model = Usuario
    template_name = 'usuario/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude(is_superuser = True)
        return queryset
    
class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'usuario/eliminar_usuario.html'
    success_url = reverse_lazy('apps.usuario:usuario_list')

    def post(self, request, *args, **kwargs):
        eliminar_comentarios = request.POST.get('eliminar_comentarios', False)
        eliminar_posts = request.POST.get('eliminar_posts', False)
        self.object = self.get_object()

        if not request.user.is_superuser:
            # Si el usuario no es superuser,mostrar un error de PermisionDenied
            raise PermissionDenied("No tienes el permiso para eliinar usuarios.")

        if eliminar_comentarios:
            Comentario.objects.filter(usuario=self.object).delete()

        if eliminar_posts:
            Post.objects.filter(usuario=self.object).delete()

        messages.success(request, f'Usuario {self.object.username} eliminado correctamente')
        return self.delete(request, *args, **kwargs)
    

@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        user = request.user

        # Eliminar los comentarios y posts del usuario si es necesario
        eliminar_comentarios = request.POST.get('eliminar_comentarios', False)
        eliminar_posts = request.POST.get('eliminar_posts', False)

        if eliminar_comentarios:
            Comentario.objects.filter(usuario=user).delete()

        if eliminar_posts:
            Post.objects.filter(usuario=user).delete()

        # Eliminar el usuario
        user.delete()

        # Redireccionar al inicio de sesión
        return redirect('apps.usuario:login')
    else:
        return render(request, 'usuario/eliminar_cuenta.html')
    

def acercaDe(request):
    return render(request, 'about.html')