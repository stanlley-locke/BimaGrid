import django
django.setup()
from django.urls import get_resolver

def get_all_urls(urllist, pre=''):
    for entry in urllist:
        if hasattr(entry, 'url_patterns'):
            get_all_urls(entry.url_patterns, pre + str(entry.pattern))
        else:
            print(pre + str(entry.pattern))

get_all_urls(get_resolver().url_patterns)
