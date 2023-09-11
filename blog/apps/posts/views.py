from django.shortcuts import render, redirect, get_object_or_404
# Asegúrate de crear este formulario
from .forms import PostForm, ComentarioForm, CategoriaForm
from .models import Post, Categoria, Comentario
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


# Create your views here.
app_name = 'apps.posts'


class PostListView(ListView):
    model = Post
    template_name = "posts/posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        # Obtener el valor del parámetro 'sort' de la URL
        sort_order = self.request.GET.get('sort', 'desc')

        # Cambiar el orden de acuerdo al valor del parámetro 'sort'
        if sort_order == 'asc':
            return Post.objects.filter(activo=True).order_by('fecha')
        elif sort_order == 'a':
            return Post.objects.filter(activo=True).order_by('titulo')
        elif sort_order == 'z':
            return Post.objects.filter(activo=True).order_by('-titulo')
        else:
            return Post.objects.filter(activo=True).order_by('-fecha')

# @method_decorator(login_required, name='dispatch')


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/postindividual.html"
    context_object_name = "posts"
    pk_url_kwarg = "id"
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ComentarioForm()
        context['comentarios'] = Comentario.objects.filter(
            posts_id=self.kwargs['id'])
        return context

    def post(self, request, *args, **kwargs):
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.posts_id = self.kwargs['id']
            comentario.save()
            return redirect('apps.posts:postindividual', id=self.kwargs['id'])
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)


class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm
    template_name = 'comentario/agregarComentario.html'
    success_url = 'comentario/comentarios'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.posts_id = self.kwargs['posts_id']
        return super().form_valid(form)


def postUser(request):
    postsUser = Post.objects.filter(usuario=request.user)
    sort_param = request.GET.get('sort')
    if sort_param == 'asc':
        postsorder = Post.objects.filter(
            usuario=request.user).order_by('fecha')
        return render(request, 'posts/Misposts.html', {'posts': postsorder})
    elif sort_param == 'desc':
        postsorder = Post.objects.filter(
            usuario=request.user).order_by('-fecha')
        return render(request, 'posts/Misposts.html', {'posts': postsorder})
    elif sort_param == 'a':
        postsorder = Post.objects.filter(
            usuario=request.user).order_by('titulo')
        return render(request, 'posts/Misposts.html', {'posts': postsorder})
    elif sort_param == 'z':
        postsorder = Post.objects.filter(
            usuario=request.user).order_by('-titulo')
        return render(request, 'posts/Misposts.html', {'posts': postsorder})
    else:
        return render(request, 'posts/Misposts.html', {'posts': postsUser})


def editarPost(request, id):
    post = get_object_or_404(Post, id=id)
    # comprueba el permiso de edicion
    if not post.puede_editar(request.user):
        messages.error(request, 'No tienes permiso para editar este post.')
        return redirect('apps.posts:postindividual', id=id)

    form = PostForm(initial={'titulo': post.titulo, 'subtitulo': post.subtitulo,
                    'texto': post.texto, 'categoria': post.categoria, 'imagen': post.imagen})
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post.titulo = form.cleaned_data['titulo']
            post.subtitulo = form.cleaned_data['subtitulo']
            post.texto = form.cleaned_data['texto']
            post.categoria = form.cleaned_data['categoria']
            post.imagen = form.cleaned_data['imagen']
            post.save()
            messages.success(request, 'El post ha sido editado correctamente.')
            return redirect('apps.posts:postindividual', id=id)

    return render(request, 'posts/editarPost.html', {'form': form, 'post': post.id})


def index(request):
    categorias = Categoria.objects.all()
    posts = Post.objects.order_by('-publicado')[:3]  # Obtener los últimos 3 posts
    return render(request, 'index.html', {'categorias': categorias, 'posts': posts})

# *Metodo para obtener Todos Los Posts de Una Categoria Especifica


def requestCategoria(request, id):
    try:
        categoria = existe_categoria(id)
        posts = Post.objects.all().filter(categoria=id)
    except Exception:
        categoria = Categoria.objects.get(id=id)
        posts = Post.objects.all().filter(categoria=id)
    context = {
        'categoria': categoria,
        'posts': posts
    }
    return render(request, 'categoria/categoria.html', context)


def existe_categoria(id):
    for i in Categoria.objects.all:
        if i.id == id:
            return i
    return None


def eliminarPost(request, id):
    post = get_object_or_404(Post, id=id)

    # Comprueba permisos de eliminación
    if not post.puede_eliminar(request.user):
        messages.error(request, 'No tienes permiso para eliminar este post.')
        return redirect('apps.posts:posts')
    ##
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'El post ha sido eliminado correctamente.')
        return redirect('apps.posts:posts')

    return render(request, 'posts/eliminarPost.html', {'post': post})


def editar_comentario(request, post_id, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    if not comentario.puede_editar(request.user):
        return redirect('apps.posts:postindividual', id=post_id)
    if request.method == 'POST':
        print('pasamos')
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            return redirect('apps.posts:postindividual', id=post_id)
    else:
        form = ComentarioForm(instance=comentario)
    return render(request, 'comentarios/editar_comentario.html', {'form': form, 'post_id': post_id})


def eliminar_comentario(request, post_id, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    if not comentario.puede_eliminar(request.user):
        return redirect('apps.posts:postindividual', id=post_id)
    if request.method == 'POST':
        comentario.delete()
        # Corregimos el nombre de la ruta aquí
        return redirect('apps.posts:postindividual', id=post_id)
    return render(request, 'comentarios/eliminar_comentario.html', {'comentario': comentario, 'post_id': post_id})

# * Vista de Agregar la Categoria


class AgregarCategoriaView(View):
    def get(self, request):
        usuario = request.user

        if usuario.is_authenticated and usuario.es_colaborador:
            form_categoria = CategoriaForm()
            return render(request, 'posts/agregar_categoria.html', {'form_categoria': form_categoria})
        else:
            return redirect('apps.posts:posts')

    def post(self, request):
        form_categoria = CategoriaForm(request.POST)
        if form_categoria.is_valid():
            form_categoria.save()
            # ? messages.success(request, 'Categoría guardada exitosamente.')  # Mensaje de confirmación

            # Limpiar el formulario de Categoria
            form_categoria = CategoriaForm()

            # Redireccionar al formulario de Post
            return redirect('apps.posts:agregar_post')
        return render(request, 'posts/agregar_categoria.html', {'form_categoria': form_categoria})

# * Clase de la


class AgregarPostView(View):

    def get(self, request):
        # Inicia el formulario con los valores anteriormente cargados o inicia con None si no hay datos en la sesión

        form_post = PostForm(
            initial=request.session.get('post_form_data', None))

        usuario = request.user

        if usuario.is_authenticated and usuario.es_colaborador:
            return render(request, 'posts/agregar_post.html', {'form_post': form_post})
        else:
            return redirect('apps.posts:posts')

    def post(self, request):
        if 'btn_post' in request.POST:
            form_post = PostForm(request.POST, request.FILES)
            if form_post.is_valid():
                post = form_post.save(commit=False)
                post.usuario = request.user
                post.save()
                post.clean()

                # Limpiar la variable de sesión solo cuando el formulario de post es válido
                request.session['post_form_data'] = None

                return redirect('apps.posts:posts')

        elif 'btn_categoria' in request.POST:
            # Guardar los datos del post en una variable de sesión para su posterior uso
            post_data = request.POST
            request.session['post_form_data'] = post_data

            return redirect('apps.posts:agregar_cate')

        # Si se presiona otro botón o se realiza otra acción, simplemente se muestra el formulario de post con los datos de la sesión
        form_post = PostForm(
            initial=request.session.get('post_form_data', None))
        return render(request, 'posts/agregar_post.html', {'form_post': form_post})