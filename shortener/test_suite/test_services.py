from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from shortener.services import calculate_expiry, generate_random_code, validate_custom_alias


class ExpirationLogicTest(TestCase):
    
    def test_anonymous_expiry_returns_30_days(self):
        expiry = calculate_expiry(user=None)
        expected = timezone.now() + timedelta(days=settings.ANON_EXPIRY_DAYS)
        delta = abs((expiry - expected).total_seconds())
        self.assertLess(delta, 2)
    
    def test_authenticated_expiry_returns_90_days(self):
        user = User.objects.create_user(username='test', email='test@test.com', password='testpass')
        expiry = calculate_expiry(user=user)
        expected = timezone.now() + timedelta(days=settings.AUTH_EXPIRY_DAYS)
        delta = abs((expiry - expected).total_seconds())
        self.assertLess(delta, 2)


class RandomCodeGenerationTest(TestCase):
    
    def test_generates_code_of_correct_length(self):
        code = generate_random_code(length=8)
        self.assertEqual(len(code), 8)
    
    def test_generates_alphanumeric_code(self):
        code = generate_random_code()
        self.assertTrue(code.isalnum())
    
    def test_generates_unique_codes(self):
        codes = [generate_random_code() for _ in range(100)]
        self.assertEqual(len(codes), len(set(codes)))


class CustomAliasValidationTest(TestCase):
    
    def test_alias_too_short_fails(self):
        valid, message = validate_custom_alias("short")
        self.assertFalse(valid)
        self.assertIn("al menos", message)
    
    def test_alias_with_special_chars_fails(self):
        valid, message = validate_custom_alias("invalid-alias!")
        self.assertFalse(valid)
        self.assertIn("letras y números", message)
    
    def test_valid_alias_passes(self):
        valid, message = validate_custom_alias("validalias123")
        self.assertTrue(valid)
        self.assertEqual(message, "")
