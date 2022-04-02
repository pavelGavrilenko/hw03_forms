from cgitb import text
from tokenize import group
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from yatube.settings import PAGINOR_COUNT_PAGE

from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_creater = User.objects.create_user(username='poster_creater')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='superslug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_creater,
            text='Тестовый пост',
        )
        for i in range(12):
            cls.post_group = Post.objects.create(
                author=cls.user_creater,
                text=f'Тестовая {i}',
                group=cls.group
            )
        # ожидаем 13 постов в базе, 1 тестовый и 12 тесовыйх с группой
        # при тетсировании любого адресса с пагинатором 1ая страница заполнена
        # лучше тестировтаь только вторую страницу. Нужно придумать алгоритм который подойдет для всех. 

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Ivan')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.creator_client = Client()
        self.creator_client.force_login(PostViewsTests.user_creater)
        self.context_post_expectation = {
            reverse('posts:index'): Post.objects.all().order_by('-pub_date'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug}
            ): Post.objects.filter(group=PostViewsTests.group).order_by('-pub_date'),
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.user_creater.username}
            ): Post.objects.filter(author=PostViewsTests.user_creater).order_by('-pub_date'),
        }
        #словарь ожиданий пока остаивм в классе, т.к его используют 2 функции, уже 3?

    def test_pages_uses_correct_template(self):
        '''Проверяем соответвие имен - вызываем шаблонам'''
        templates_pages_names_expectation = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTests.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTests.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names_expectation.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.creator_client.get(reverse_name)
                self.assertTemplateUsed(response, template, 'Проблема шаблона по спейснейму')

    def test_context_post_expectation_on_1st_paginator_page(self):
        '''Проверяем контектс на первой заполненой странице пагинатора'''
        for reverse_name, expectation in self.context_post_expectation.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.creator_client.get(reverse_name)
                expectation_result = list(expectation[:PAGINOR_COUNT_PAGE])
                self.assertEqual(response.context.get('page_obj').object_list, expectation_result, 'Контексттрабл')

    def test_context_post_expectation_on_1st_paginator_page(self):
        '''Проверяем что пагинатор по второй странице отоборжает ожидаемое число постов'''
        for reverse_name, expectation in self.context_post_expectation.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.creator_client.get(reverse_name + '?page=2')
                page2_count_expectation = (len(list(expectation))) - PAGINOR_COUNT_PAGE
                self.assertEqual(len(response.context.get('page_obj').object_list), page2_count_expectation, 'Другое количество постов на второй странице пагинатора')

    def test_post_detail_have_1_post(self):
        '''Проверяем что детальный пост содержит 1 пост по id'''
        response = self.creator_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': PostViewsTests.post.pk})
        )
        expectation = get_object_or_404(Post, pk=PostViewsTests.post.pk)
        self.assertEqual(response.context.get('post'), expectation, 'В деталях поста не тот пост')

    def test_post_create_have_form(self):
        '''Проверяем что при создании поста передается форма и тип ее полей'''
        response = self.creator_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_have_old_value(self):
        '''Проверяем что отображается форма редактирования со старыми данными в ней'''
        response = self.creator_client.get(
            reverse('posts:post_edit', kwargs={'post_id': PostViewsTests.post.pk})
        )
        old_text = response.context['form']['text'].value()
        old_group = response.context['form']['group'].value()
        self.assertEqual(old_text, PostViewsTests.post.text)
        self.assertEqual(old_group, PostViewsTests.post.group)

    def test_create_another_post(self):
        '''Создаем пост в новой группе, проверяем его на главной, групповой и в профайле '''
        group_new = Group.objects.create(
            title='Дополнительная группа',
            slug='2',
            description='Для финального задания',
        )
        post_new = Post.objects.create(
            author=self.user,
            text='Пост от ивана в новуб группу',
            group=group_new
        )
        exepmle_list_for_new_post = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': group_new.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        ]
        for reverse_name in exepmle_list_for_new_post:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertIn(post_new, response.context.get('page_obj').object_list)
        # допольнительная проверка что нового поста нет в старой группе
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug}
            )
        )
        self.assertNotIn(post_new, response.context.get('page_obj').object_list)

