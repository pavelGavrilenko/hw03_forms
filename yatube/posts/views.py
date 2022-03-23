from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Group, Post
from .utils import paginator

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = paginator(request, post_list)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = page_obj = paginator(request, post_list)
    title = f'Записи сообщества {group.title}'
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    title = f'Профайл пользователя {username}'
    author = get_object_or_404(User, username=username)
    count = Post.objects.filter(
        author=author
    ).count()
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    page_obj = page_obj = paginator(request, post_list)
    context = {
        'author': author,
        'title': title,
        'username': username,
        'count': count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.author.posts.count()
    context = {
        'post': post,
        'count': count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    title = 'Новый пост'
    context = {
        'form': form,
        'title': title,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author_post = post.author
    if request.user != author_post:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    title = 'Редактирование поста'
    is_edit = True
    context = {
        'form': form,
        'title': title,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)
