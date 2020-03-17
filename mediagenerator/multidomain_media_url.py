import os, os.path
import urlparse

from django.conf import settings
from django.core.files.storage import FileSystemStorage

count = 0
media_count=100
def rewrite_url():
    media_change = getattr(settings, 'CHANGE_MEDIA_URL', False)
    if (media_change):
        global count
        global media_count
        count += 1
        if count == 5:
            media_count += 1
            count = 0
        url_pattern = settings.MEDIA_URL_PATTERN
        return url_pattern.replace('%d', str(media_count))
    else:
        return ''
    
class CustomFileSystemStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location = os.path.abspath(location)
        self.base_url = urlparse.urljoin(rewrite_url(), base_url)

