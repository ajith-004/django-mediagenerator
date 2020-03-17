from django.conf import settings
from django.utils.encoding import smart_str
from mediagenerator.generators.bundles.base import Filter

class GzipCompressor(Filter):
    def __init__(self, **kwargs):
        super(GzipCompressor, self).__init__(**kwargs)
        assert self.filetype in ('css', 'js'), (
            'GzipCompressor only supports compilation to css and js. '
            'The parent filter expects "%s".' % self.filetype)

    # def get_variations(self):
    #     # we can generate variations such as gzipped and non-gzipped
    #     return {
    #         'compression': ['regular', 'compressed']
    #     }

    def get_output(self, variation):
        # We import this here, so App Engine Helper users don't get import
        # errors.
        from subprocess import Popen, PIPE
        for input in self.get_input(variation):
            try:
                cmd = Popen(['gzip', '--best'],
                            stdin=PIPE, stdout=PIPE, stderr=PIPE,
                            universal_newlines=True)
                output, error = cmd.communicate(smart_str(input))
                assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
                yield output #this is the final filter, so we output str and not unicode
            except Exception, e:
                raise ValueError("Failed to execute GZip compressor %s" % e)
