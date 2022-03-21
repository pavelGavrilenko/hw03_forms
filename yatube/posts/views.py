from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .forms import PostForm

from .models import Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Записи сообщества {group.title}'
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    title = f'Профайл пользователя {username}'
    author = User.objects.get(username=username)
    count = Post.objects.filter(
        author=author
    ).count()
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'title': title,
        'username': username,
        'count': count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    title = Post.objects.get(pk=post_id)
    post = Post.objects.get(pk=post_id)
    count = post.author.posts.count()
    context = {
        'title': title,
        'post': post,
        'count': count,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            author = User.objects.get(username=request.user)
            Post.objects.create(text=text, group=group, author=author)
            return redirect('posts:profile', author)
        return render(request, 'posts/create_post.html')

    form = PostForm()
    title = 'Новый пост'
    context = {
        'form': form,
        'title': title,
    }
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    author_post = post.author
    if request.user != author_post:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id)

    form = PostForm(instance=post)
    title = 'Редактирование поста'
    is_edit = True
    context = {
        'form': form,
        'title': title,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)
