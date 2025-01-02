from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.utils import timezone
from .forms import PostCreationForm, UserEditForm, CommentCreationForm
from .models import Post, Category, Comment


User = get_user_model()


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)  # Получаем пост по ID

    if request.method == 'POST':
        form = CommentCreationForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CommentCreationForm()

    return render(request, 'detail.html', {'form': form, 'post': post})


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentCreationForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentCreationForm(instance=comment)
    return render(
        request, 'blog/comment.html', {'form': form, 'comment': comment}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html', {'comment': comment}
    )


class ProfileView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        posts = (
            Post.objects
            .filter(author=profile_user.id)
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')

        context['profile'] = profile_user
        context['user'] = self.request.user
        context['page_obj'] = paginator.get_page(page_number)

        return context


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', request.user)
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


@login_required()
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostCreationForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostCreationForm(instance=post)
    return render(
        request, 'blog/create.html', {'form': form, 'post': post}
    )


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(
        request,
        'blog/create.html',
        {'post': post, 'form': PostCreationForm(instance=post)}
    )


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostCreationForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostCreationForm()
    return render(request, 'blog/create.html', {'form': form})


class PostListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'
    queryset = (
        Post.objects
        .filter(
            pub_date__lt=timezone.now(),
            is_published__exact=True,
            category__is_published=True
        )
        .select_related('category')
        .annotate(comment_count=Count('comments'))
    )


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs['post_id']
        post = get_object_or_404(
            Post,
            id=post_id
        )
        if post.author == self.request.user:
            context['post'] = post
        else:
            if (
                post.is_published
                and post.category.is_published
                and post.pub_date < timezone.now()
            ):
                context['post'] = post
            else:
                raise Http404("Пост не найден или недоступен")
        context['comments'] = Comment.objects.filter(post=post_id)
        context['post'] = post
        context['form'] = CommentCreationForm()
        return context


def category_posts(request, category_slug):
    """Отображение публикаций категории"""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = Post.objects.filter(
        category=category.id,
        is_published=True,
        pub_date__lt=timezone.now()
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category}
    if posts:
        context['page_obj'] = page_obj
    else:
        context['page_obj'] = []
    template = 'blog/category.html'
    return render(request, template, context=context)
