from django.conf import settings
from mediagenerator.base import Generator
from mediagenerator import utils, settings as mg_settings
from hashlib import sha1
import Image
from StringIO import StringIO
import os

MEDIA_SPRITES = getattr(settings, 'MEDIA_SPRITES', ())
MEDIA_URL = mg_settings.MEDIA_DEV_MODE and mg_settings.DEV_MEDIA_URL or mg_settings.PRODUCTION_MEDIA_URL

class Sprites(Generator):
    cache = {}
    padding = 10

    def get_dev_output(self, name):
        return self.cache[name]

    def get_dev_output_names(self):
        for items in MEDIA_SPRITES:
            sprite_name = items[0]
            sprite_css_name, sprite_png_name, hash = self.generate(sprite_name, items[1:])

            yield sprite_css_name, sprite_css_name, hash
            yield sprite_png_name, sprite_png_name, hash

    def generate(self, sprite_name, image_names):
        sprite_css_name, sprite_png_name = sprite_name + '.sprite.css', sprite_name + '.sprite.png'
        matrix = []

        for img in image_names:
            im = Image.open(utils.find_file(img))
            matrix.append((im.size[1], [(im.size[0], img, im)]))
            matrix.append((self.padding, ()))

        w = max((sum((j[0] for j in i[1])) for i in matrix))
        h = sum((i[0] for i in matrix))

        css = ""
        sprite = Image.new("RGBA", (w,h))
        y = 0
        for i in matrix:
            x, h = 0, i[0]
            for j in i[1]:
                w = j[0]
                sprite.paste(j[2], (x,y))
                selector = os.path.splitext(j[1])[0].replace(os.path.sep, '_')
                css += "\n.%s.%s { background-position: %dpx %dpx; }" % (sprite_name, selector, -x,-y)
                css += "\n.%s.%s.sized { width: %dpx; height: %dpx; }" % (sprite_name, selector, w,h)
                css += "\n.%s.%s.replace { overflow: hidden; text-indent: -9999px; width: %dpx; height: %dpx;}" % (sprite_name, selector, w,h)
                x += w
            y += h

        buf = StringIO()
        sprite.save(buf, format="PNG")
        png = buf.getvalue()
        buf.close()

        hash = sha1(png).hexdigest()

        self.cache[sprite_css_name] = css, "text/css"
        self.cache[sprite_png_name] = png, "image/png"
        return sprite_css_name, sprite_png_name, hash
