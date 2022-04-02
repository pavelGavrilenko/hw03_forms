from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
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
            text='Тестовая пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Ivan')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.creator_client = Client()
        self.creator_client.force_login(PostURLTests.user_creater)
        self.pull_pages_to_unauthorized = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.pk}/': 'posts/post_detail.html',
            '/not_foind_page/': None,
        }

    def test_accessibility_of_pages_to_unauthorized(self):
        for url in self.pull_pages_to_unauthorized.keys():
            response = self.guest_client.get(url)
            if url == '/not_foind_page/':
                self.assertEqual(response.status_code, 404)
            else:
                with self.subTest(url=url):
                    self.assertEqual(response.status_code, 200)

    def test_auththorized_not_author_redirect_edit(self):
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{PostURLTests.post.pk}/')

    def test_author_must_edit(self):
        response = self.creator_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, 200)

    def test_unautorized_dont_create(self):
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_autorized_user_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_template_for_all_user(self):
        for adress, template in self.pull_pages_to_unauthorized.items():
            response = self.guest_client.get(adress)
            if adress == '/not_foind_page/':
                self.assertEqual(response.status_code, 404)
            else:
                with self.subTest(adress=adress):
                    self.assertTemplateUsed(response, template)

    def test_auththorized_not_edit_template(self):
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_author_must_edit_template(self):
        response = self.creator_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/'
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_unautorized_dont_create_template(self):
        response = self.guest_client.get(
            '/create/',
            follow=True
        )
        self.assertTemplateUsed(response, 'users/login.html')

    def test_autorized_user_create_template(self):
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
