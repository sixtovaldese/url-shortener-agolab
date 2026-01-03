from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from shortener.models import ShortLink
from shortener.services import calculate_expiry, generate_random_code


class ShortLinkModelTest(TestCase):
    
    def test_create_anonymous_link(self):
        code = generate_random_code()
        expiry = calculate_expiry()
        link = ShortLink.objects.create(
            original_url='https://example.com',
            short_code=code,
            expires_at=expiry
        )
        self.assertIsNone(link.owner)
        self.assertEqual(link.click_count, 0)
    
    def test_create_authenticated_link(self):
        user = User.objects.create_user(username='test', email='test@test.com', password='testpass')
        code = 'mycustomcode123'
        expiry = calculate_expiry(user=user)
        link = ShortLink.objects.create(
            original_url='https://example.com',
            short_code=code,
            owner=user,
            expires_at=expiry
        )
        self.assertEqual(link.owner, user)
    
    def test_is_expired_returns_true_for_past_date(self):
        link = ShortLink.objects.create(
            original_url='https://example.com',
            short_code='test123',
            expires_at=timezone.now() - timezone.timedelta(days=1)
        )
        self.assertTrue(link.is_expired())
    
    def test_is_expired_returns_false_for_future_date(self):
        link = ShortLink.objects.create(
            original_url='https://example.com',
            short_code='test123',
            expires_at=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertFalse(link.is_expired())
