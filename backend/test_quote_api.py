import django
django.setup()
from django.test.client import Client
from apps.accounts.models import Profile
from rest_framework.authtoken.models import Token

c = Client()
profile = Profile.objects.first()
token, _ = Token.objects.get_or_create(user=profile.user)
res = c.post('/api/v1/pricing/quote/', {"crop":"MAIZE","acreage":2.5,"h3_index":"8928308280fffff"}, HTTP_AUTHORIZATION=f'Token {token.key}', content_type="application/json")
print("Status:", res.status_code)
print("Content:", res.content)
