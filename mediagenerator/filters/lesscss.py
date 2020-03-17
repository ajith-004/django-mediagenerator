from hashlib import sha1
from mediagenerator.settings import ENABLE_LESS_CSS_CLEAN_CSS, ENABLE_LESS_CSS_DEBUG
from mediagenerator.generators.bundles.base import Filter
from mediagenerator.utils import find_file
from subprocess import Popen, PIPE
import os, sys

class LessCSS(Filter):
    """
    LessCSS filter
    You need node.js and lessc on your path
    """

    takes_input = False

    def __init__(self, **kwargs):
        self.config(kwargs, module=None)
        super(LessCSS, self).__init__(**kwargs)
        assert self.filetype == 'css', (
            'LessCSS only supports compilation to css. '
            'The parent filter expects "%s".' % self.filetype)
        self._compiled = None
        self._compiled_hash = None
        self._mtime = None
        
        #handling LessCSS imports
        self._root_path = '/'.join(self.module.split('/')[:-1])
        self._imports = None
        self._imports_code = {}

    @classmethod
    def from_default(cls, name):
        return {'module': name}

    def get_output(self, variation):
        self._regenerate(debug=False)
        yield self._compiled

    def get_dev_output(self, name, variation):


        assert name == self.module or name in self._imports
        self._regenerate(debug=True)
        if name == self.module:
            return self._compiled
        elif name in self._imports:
            return self._imports_code[name]

    def get_dev_output_names(self, variation):
        self._regenerate(debug=True)
        yield self.module, self._compiled_hash

        if self._imports:
            for name in self._imports:
                yield name, self._compiled_hash

    def _regenerate(self, debug=False):
        path = find_file(self.module)
        mtime = os.path.getmtime(path)
        # the following fails, if files "imported" into the current less file have been
        # modified; disable this temporarily
        # if mtime == self._mtime:
        #     print "*** no need to regenerate", path, mtime, self._mtime
        #     return
        if not debug or not ENABLE_LESS_CSS_DEBUG:
            self._compiled = self._compile(path, debug=debug)
            self._compiled_hash = sha1(self._compiled).hexdigest()
            self._compiled = self._compiled.decode('utf-8') #decoding it here as sha1 expects str
            self._mtime = mtime
        else:
            self._compiled = file(path).read()
            self._extract_imports(self._compiled)
            self._imports_code = {name: file(find_file(name)).read().decode('utf-8') for name in self._imports}
            self._compiled_hash = 'kane'
            self._compiled = self._compiled.decode('utf-8')
            self._mtime = mtime


    def _extract_imports(self, code):
        import re
        p = re.compile(ur'@import "(.+)";')

        self._imports = []
         
        matches = re.findall(p, code)
        if matches:
            for x in matches:
                self._imports.append(self._root_path+'/'+x)

    def _compile(self, path, debug=False):
        try:
            filepath, filename = os.path.split(path)
            command = ['lessc', '-x', '--verbose']
            if ENABLE_LESS_CSS_CLEAN_CSS:
                #for some reason, it does not load the clean-css plugin at this point
                command.append('--clean-css="advanced"')
            command.append(filename)
            cmd = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        shell=False, universal_newlines=True, cwd=filepath)
            output, error = cmd.communicate("")
            assert cmd.wait() == 0, ('LessCSS command returned bad '
                                     'result:\n%s' % error)
            return output #this actually returns an str and not unicode; is decoded in _regenerate above
        except Exception, e:
            raise ValueError("Failed to run LessCSS compiler for this "
                "file. Please confirm that the \"lessc\" application is "
                "on your path and that you can run it from your own command "
                "line.\n"\
                "File: %s\n"\
                "Error was: %s" % (path, e))
