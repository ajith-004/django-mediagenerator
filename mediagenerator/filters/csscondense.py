from django.conf import settings
from django.utils.encoding import smart_str
from mediagenerator.generators.bundles.base import Filter

class CSSCondenseCompressor(Filter):
    def __init__(self, **kwargs):
        super(CSSCondenseCompressor, self).__init__(**kwargs)
        assert self.filetype in ('css'), (
            'CSSCondenseCompressor only supports compilation of css. '
            'The parent filter expects "%s".' % self.filetype)

    def get_output(self, variation):
        # We import this here, so App Engine Helper users don't get import
        # errors.
        from subprocess import Popen, PIPE
        for input in self.get_input(variation):
            try:
                cmd = Popen(['cssc', '--safe', '--line-breaks'],
                            stdin=PIPE, stdout=PIPE, stderr=PIPE,
                            universal_newlines=True)
                output, error = cmd.communicate(smart_str(input))
                assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
                yield output.decode('utf-8')
            except Exception, e:
                raise ValueError("Failed to execute uglifyjs. "
                    "Please make sure that you have installed css-condense "
                    "and that it's in your PATH and that you've configured "
                    "your settings correctly.\n"
                    "Error was: %s" % e)

