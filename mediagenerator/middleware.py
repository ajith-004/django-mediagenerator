from .settings import DEV_MEDIA_URL, MEDIA_DEV_MODE
# Only load other dependencies if they're needed
if MEDIA_DEV_MODE:
    from .utils import _refresh_dev_names, _backend_mapping
    from django.http import HttpResponse, Http404
    from django.utils.cache import patch_cache_control
    from django.utils.http import http_date
    import time

    _REFRESH_DEV_NAMES_DONE_AT = 0

TEXT_MIME_TYPES = (
    'application/x-javascript',
    'application/xhtml+xml',
    'application/xml',
)

class MediaMiddleware(object):
    """
    Middleware for serving and browser-side caching of media files.

    This MUST be your *first* entry in MIDDLEWARE_CLASSES. Otherwise, some
    other middleware might add ETags or otherwise manipulate the caching
    headers which would result in the browser doing unnecessary HTTP
    roundtrips for unchanged media.
    """

    MAX_AGE = 60 * 60 * 24 * 365

    def process_request(self, request):
        if not MEDIA_DEV_MODE:
            return

        # We refresh the dev names only once every 30 seconds, so all
        # media_url() calls are cached.
        # This allows for every "page load" to go very quickly, but does not require a
        # server restart to get new file paths and versions.
        global _REFRESH_DEV_NAMES_DONE_AT
        if (_REFRESH_DEV_NAMES_DONE_AT + 15) < time.time():
            print "*** refreshing media files dev_names", _REFRESH_DEV_NAMES_DONE_AT
            _refresh_dev_names()
            _REFRESH_DEV_NAMES_DONE_AT = time.time()

        if not request.path.startswith(DEV_MEDIA_URL):
            return

        filename = request.path[len(DEV_MEDIA_URL):]

        try:
            backend = _backend_mapping[filename]
        except KeyError:
            raise Http404('The mediagenerator could not find the media file "%s"'
                          % filename)
        content, mimetype = backend.get_dev_output(filename)
        if not mimetype:
            mimetype = 'application/octet-stream'
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        if mimetype.startswith('text/') or mimetype in TEXT_MIME_TYPES:
            mimetype += '; charset=utf-8'
        response = HttpResponse(content, content_type=mimetype)
        response['Content-Length'] = len(content)

        # Cache manifest files MUST NEVER be cached or you'll be unable to update
        # your cached app!!!
        if response['Content-Type'] != 'text/cache-manifest' and \
                response.status_code == 200:
            ## Cannot cache LessCSS files this way for less.watch to work
            # patch_cache_control(response, public=True, max_age=self.MAX_AGE)
            # response['Expires'] = http_date(time.time() + self.MAX_AGE)
            pass
        return response
