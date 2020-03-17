from django.conf import settings
from django.utils.encoding import smart_str
from mediagenerator.generators.bundles.base import Filter

class NullCompressor(Filter):
    def __init__(self, **kwargs):
        super(NullCompressor, self).__init__(**kwargs)
        assert self.filetype in ('js', 'css'), (
            'NullCompressor only supports compilation of css and js. '
            'The parent filter expects "%s".' % self.filetype)

    def get_output(self, variation):
        for input in self.get_input(variation):
            yield input


