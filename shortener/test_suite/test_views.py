from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from shortener.models import ShortLink
from shortener.services import calculate_expiry


class HomeViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_home_page_loads(self):
        response = self.client.get(reverse('shortener:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acorta tus URLs')
    
    def test_create_anonymous_link(self):
        response = self.client.post(reverse('shortener:home'), {
            'url': 'https://example.com/test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ShortLink.objects.count(), 1)
        link = ShortLink.objects.first()
        self.assertIsNone(link.owner)
        self.assertEqual(link.original_url, 'https://example.com/test')
    
    def test_anonymous_cannot_use_custom_alias(self):
        response = self.client.post(reverse('shortener:home'), {
            'url': 'https://example.com/test',
            'alias': 'customalias123'
        })
        self.assertEqual(ShortLink.objects.count(), 0)
        self.assertContains(response, 'iniciar sesión')
    
    def test_authenticated_can_use_custom_alias(self):
        user = User.objects.create_user(username='test', email='test@test.com', password='testpass123')
        self.client.login(username='test', password='testpass123')
        
        response = self.client.post(reverse('shortener:home'), {
            'url': 'https://example.com/test',
            'alias': 'customalias123'
        })
        self.assertEqual(ShortLink.objects.count(), 1)
        link = ShortLink.objects.first()
        self.assertEqual(link.short_code, 'customalias123')
        self.assertEqual(link.owner, user)
    
    def test_custom_alias_too_short_fails(self):
        user = User.objects.create_user(username='test', email='test@test.com', password='testpass123')
        self.client.login(username='test', password='testpass123')
        
        response = self.client.post(reverse('shortener:home'), {
            'url': 'https://example.com/test',
            'alias': 'short'
        })
        self.assertEqual(ShortLink.objects.count(), 0)
        self.assertContains(response, 'al menos')
    
    def test_duplicate_alias_fails(self):
        user = User.objects.create_user(username='test', email='test@test.com', password='testpass123')
        ShortLink.objects.create(
            original_url='https://example.com/first',
            short_code='existingalias',
            owner=user,
            expires_at=calculate_expiry(user)
        )
        self.client.login(username='test', password='testpass123')
        
        response = self.client.post(reverse('shortener:home'), {
            'url': 'https://example.com/second',
            'alias': 'existingalias'
        })
        self.assertEqual(ShortLink.objects.count(), 1)
        self.assertContains(response, 'ya está en uso')


class RedirectViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.link = ShortLink.objects.create(
            original_url='https://example.com/destination',
            short_code='test123',
            expires_at=calculate_expiry()
        )
    
    def test_redirect_works(self):
        response = self.client.get(reverse('shortener:redirect', args=['test123']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://example.com/destination')
    
    def test_redirect_increments_counter(self):
        initial_count = self.link.click_count
        self.client.get(reverse('shortener:redirect', args=['test123']))
        self.link.refresh_from_db()
        self.assertEqual(self.link.click_count, initial_count + 1)
    
    def test_nonexistent_code_returns_404(self):
        response = self.client.get(reverse('shortener:redirect', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)
    
    def test_expired_link_returns_404(self):
        from django.utils import timezone
        expired_link = ShortLink.objects.create(
            original_url='https://example.com/expired',
            short_code='expired123',
            expires_at=timezone.now() - timezone.timedelta(days=1)
        )
        response = self.client.get(reverse('shortener:redirect', args=['expired123']))
        self.assertEqual(response.status_code, 404)
