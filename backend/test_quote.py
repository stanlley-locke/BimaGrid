import django
django.setup()
from apps.pricing.services import calculate_quote
from apps.accounts.models import Profile

profile = Profile.objects.first()
try:
    q = calculate_quote(profile, {"crop":"MAIZE","acreage":2.5,"h3_index":"8928308280fffff"})
    print("Success:", q.final_premium)
except Exception as e:
    print("Error:", type(e), str(e))
