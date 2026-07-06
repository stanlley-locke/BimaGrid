import django
django.setup()
from django.test.client import Client
from apps.accounts.models import Profile
import re

c = Client()
res = c.post('/api/v1/pricing/quote/', {"crop":"MAIZE","acreage":2.5,"h3_index":"8928308280fffff"}, content_type="application/json")
content = res.content.decode('utf-8')
m = re.search(r'<title>(.*?)</title>', content)
if m: print("Title:", m.group(1))
