import builtins
import math
import numpy as np
import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.lines as mlines
import matplotlib.transforms as transforms
import random as rand


def to_plt_color(args):
    max_value = 255.0
    color = None
    if len(args) == 1:
        r = args[0]
        g = args[0]
        b = args[0]
        color = (r / max_value, g / max_value, b / max_value)
    elif len(args) == 2:
        r = args[0]
        g = args[0]
        b = args[0]
        a = args[1]
        color = (r / max_value, g / max_value, b / max_value, a / max_value)
    elif len(args) == 3:
        r = args[0]
        g = args[1]
        b = args[2]
        color = (r / max_value, g / max_value, b / max_value)
    elif len(args) == 4:
        r = args[0]
        g = args[1]
        b = args[2]
        a = args[3]
        color = (r / max_value, g / max_value, b / max_value, a / max_value)
    else:
        assert False
    return color

# from https://github.com/Abdur-rahmaanJ/ppython
def random(*args):
    if len(args) == 0:
        return rand.random()
    elif len(args) == 1:
        endnum = args[0]
        return rand.random() * endnum
    elif len(args) == 2:
        s = args[0]
        e = args[1]
        return rand.random() * (e - s) + s

def dist(x1, y1, x2, y2):
    squared_delta_x = (x2 - x1) ** 2
    squared_delta_y = (y2 - y1) ** 2
    return sqrt(squared_delta_x + squared_delta_y)

def lerp(start, stop, amt):
    return (stop - start) * amt + start

def cos(angle):
    return math.cos(angle)

def sin(angle):
    return math.sin(angle)

def radians(degrees):
    return degrees / 180.0 * math.pi

class PFont:
    def __init__(self, name):
        self.name = name

class PatchCache:
    def __init__(self, ax):
        self.ax = ax
        self.patches = []
        self.updates = []
        self.cache = None
        self._background = None

    def begin(self):
        self.updates = []

    def flush(self):
        if self.cache is None:
            return
        remainps = [cp for _, cp in self.cache]
        [rp.remove() for rp in reversed(remainps)]
        self.cache = None

    def clear(self):
        self.cache = self.patches
        self.patches = []
        self.updates = []

    def add_rect(self, x, y, w, h, kwargs):
        cached = self._get_cache('rect')
        if cached is not None:
            changed = False
            oldx, oldy = cached.get_xy()
            if oldx != x or oldy != y:
                cached.set_xy((x, y))
                changed = True
            if cached.get_width() != w:
                cached.set_width(w)
                changed = True
            if cached.get_height() != h:
                cached.set_height(h)
                changed = True
            if self._set_kwargs(cached, kwargs):
                changed = True
            p = cached
            if changed:
                self.updates.append(p)
        else:
            rect = patches.Rectangle((x, y), w, h, **kwargs)
            p = self.ax.add_patch(rect)
            self.updates.append(p)
        self.patches.append(('rect', p))

    def add_ellipse(self, x, y, w, h, kwargs):
        cached = self._get_cache('ellipse{},{}'.format(w, h))
        if cached is not None:
            cached.set_center((x, y))
            self._set_kwargs(cached, kwargs)
            p = cached
        else:
            p = patches.Ellipse((x, y), w, h, **kwargs)
            p = self.ax.add_patch(p)
        self.patches.append(('ellipse{},{}'.format(w, h), p))
        self.updates.append(p)

    def add_polygon(self, xy, closed, kwargs):
        cached = self._get_cache('polygon')
        if cached is not None:
            cached.set_xy(xy)
            cached.set_closed(closed)
            self._set_kwargs(cached, kwargs)
            p = cached
        else:
            p = patches.Polygon(xy,
                                closed=closed,
                                **kwargs)
            p = self.ax.add_patch(p)
        self.patches.append(('polygon', p))
        self.updates.append(p)

    def _get_cache(self, typename):
        if self.cache is None or len(self.cache) == 0:
            return None
        cachetype, p = self.cache.pop(0)
        if cachetype == typename:
            return p
        # Remove all cached objects when any requested objects not found
        remainps = [cp for _, cp in self.cache] + [p]
        [rp.remove() for rp in reversed(remainps)]
        self.cache = None
        return None

    def _set_kwargs(self, patch, kwargs):
        changed = False
        for k, v in kwargs.items():
            if getattr(patch, 'get_{}'.format(k))() == v:
                continue
            getattr(patch, 'set_{}'.format(k))(v)
            changed = True
        return changed

class DrawingContextBase:
    def __init__(self):
        self.CLOSE = 1
        self.P2D = 1
        self.P3D = 2
        self.LEFT = 1
        self.CENTER = 2
        self.RIGHT = 3
        self.TOP = 4
        self.BOTTOM = 5
        self.BASELINE = 6

class DrawingContext(DrawingContextBase):
    def __init__(self, fig, ax, figsize):
        super().__init__()
        self.fig = fig
        self.ax = ax
        self.width, self.height = figsize
        self.patches = PatchCache(ax)
        self._antialiased = True
        self._fill = (1.0, 1.0, 1.0)
        self._stroke = (0.0, 0.0, 0.0)
        self._strokeSize = 1
        self._points = []
        self._transforms = []
        self._currentTransform = None
        self._textAlignX = 'left'
        self._textAlignY = 'baseline'

    def clear(self):
        self._transforms = []
        self._currentTransform = None
        self.patches.begin()

    def flush(self):
        self.patches.flush()

    def _to_patch_args(self, line=False):
        args = {'antialiased': self._antialiased}
        if not line:
            if self._fill is not None:
                args['facecolor'] = self._fill
                args['fill'] = True
            else:
                args['fill'] = False
        if self._stroke is not None:
            args['linewidth'] = self._strokeSize
            args['edgecolor' if not line else 'color'] = self._stroke
        else:
            args['linewidth'] = 0
        if self._currentTransform is not None:
            trans, rotate = self._currentTransform
            args['transform'] = rotate + trans + self.ax.transData
        return args

    def background(self, *args):
        [t.remove() for t in reversed(self.fig.texts)]
        self.ax.lines.clear()
        self.patches.clear()
        self.patches.add_rect(0, 0, self.width, self.height, {
            'facecolor': to_plt_color(args)
        })

    def fill(self, *args):
        color = to_plt_color(args)
        self._fill = color

    def stroke(self, *args):
        color = to_plt_color(args)
        self._stroke = color

    def strokeSize(self, thickness):
        self._strokeSize = thickness

    def noStroke(self):
        self._stroke = None

    def noFill(self):
        self._fill = None

    def noSmooth(self):
        self._antialiased = False

    def rect(self, x, y, w, h):
        self.patches.add_rect(x, y, w, h, self._to_patch_args())

    def ellipse(self, x, y, w, h):
        self.patches.add_ellipse(x, y, w, h, self._to_patch_args())

    def line(self, x1, y1, x2, y2):
        line = mlines.Line2D([x1, x2], [y1, y2], **self._to_patch_args(line=True))
        self.ax.add_line(line)

    def beginShape(self):
        self._points = []

    def vertex(self, x, y):
        self._points.append((x, y))

    def endShape(self, mode=None):
        self.patches.add_polygon([[x, y] for x, y in self._points],
                                 closed=mode == self.CLOSE,
                                 kwargs=self._to_patch_args())

    def size(self, width, height, mode=None):
        if mode is None:
            mode = self.P2D
        assert mode != self.P3D, 'Not supported'
        self.ax.set_xlim(0, width)
        self.ax.set_ylim(0, height)
        self.ax.set_aspect(1)
        builtins.width = width
        self.width = width
        builtins.height = height
        self.height = height

    def pushMatrix(self):
        self._transforms.append(self._currentTransform)
        if self._currentTransform is not None:
            trans, rotate = self._currentTransform
            self._currentTransform = (transforms.Affine2D(trans.get_matrix()), transforms.Affine2D(rotate.get_matrix()))

    def popMatrix(self):
        self._currentTransform = self._transforms.pop()

    def translate(self, dx, dy):
        trans, rotate = self._getTransform()
        trans.translate(dx, dy)

    def rotate(self, theta):
        trans, rotate = self._getTransform()
        rotate.rotate(theta)

    def _getTransform(self):
        if self._currentTransform is None:
            self._currentTransform = (transforms.Affine2D(), transforms.Affine2D())
        return self._currentTransform

    def createFont(self, name, size=None, smooth=None, charset=None):
        pass

    def textAlign(self, alignX, alignY):
        halign = {self.LEFT: 'left', self.CENTER: 'center', self.RIGHT: 'right'}
        valign = {self.TOP: 'top', self.CENTER: 'center', self.BOTTOM: 'bottom', self.BASELINE: 'baseline'}
        self._textAlignX = halign[alignX]
        self._textAlignY = 'baseline' if alignY is None else valign[alignY]

    def text(self, *args):
        if len(args) == 3:
            self.ax.text(args[1], args[2], args[0],
                         color=self._fill,
                         horizontalalignment=self._textAlignX,
                         verticalalignment=self._textAlignY)
        else:
            assert False

class DrawingContextProxy(DrawingContextBase):
    def __init__(self):
        super().__init__()
        self.base = None

    def clear(self):
        if self.base is None:
            return
        self.base.clear()

    def flush(self):
        if self.base is None:
            return
        self.base.flush()

    def background(self, *args):
        if self.base is None:
            return
        self.base.background(*args)

    def fill(self, *args):
        if self.base is None:
            return
        self.base.fill(*args)

    def stroke(self, *args):
        if self.base is None:
            return
        self.base.stroke(*args)

    def strokeSize(self, thickness):
        if self.base is None:
            return
        self.base.strokeSize(thickness)

    def noStroke(self):
        if self.base is None:
            return
        self.base.noStroke()

    def noFill(self):
        if self.base is None:
            return
        self.base.noFill()

    def noSmooth(self):
        if self.base is None:
            return
        self.base.noSmooth()

    def rect(self, x, y, w, h):
        if self.base is None:
            return
        self.base.rect(x, y, w, h)

    def ellipse(self, x, y, w, h):
        if self.base is None:
            return
        self.base.ellipse(x, y, w, h)

    def line(self, x1, y1, x2, y2):
        if self.base is None:
            return
        self.base.line(x1, y1, x2, y2)

    def beginShape(self):
        if self.base is None:
            return
        self.base.beginShape()

    def vertex(self, x, y):
        if self.base is None:
            return
        self.base.vertex(x, y)

    def endShape(self, mode=None):
        if self.base is None:
            return
        self.base.endShape(mode=mode)

    def size(self, width, height, mode=None):
        if self.base is None:
            builtins.width = width
            builtins.height = height
            return
        self.base.size(width, height, mode)

    def pushMatrix(self):
        if self.base is None:
            return
        self.base.pushMatrix()

    def popMatrix(self):
        if self.base is None:
            return
        self.base.popMatrix()

    def translate(self, dx, dy):
        if self.base is None:
            return
        self.base.translate(dx, dy)

    def rotate(self, theta):
        if self.base is None:
            return
        self.base.rotate(theta)

    def createFont(self, name, size=None, smooth=None, charset=None):
        if self.base is None:
            return None
        return self.base.createFont(name, size, smooth, charset)

    def textAlign(self, alignX, alignY=None):
        if self.base is None:
            return
        self.base.textAlign(alignX, alignY)

    def text(self, *args):
        if self.base is None:
            return
        self.base.text(*args)

def generate_functions(ctx):
    def textFont_(which, size=None):
        pass

    def textSize_(size):
        pass

    def textLeading_(leading):
        pass

    functions = {
        'background': ctx.background,
        'random': random,
        'fill': ctx.fill,
        'stroke': ctx.stroke,
        'noFill': ctx.noFill,
        'noStroke': ctx.noStroke,
        'strokeSize': ctx.strokeSize,
        'rect': ctx.rect,
        'ellipse': ctx.ellipse,
        'line': ctx.line,
        'beginShape': ctx.beginShape,
        'vertex': ctx.vertex,
        'endShape': ctx.endShape,
        'size': ctx.size,
        'noSmooth': ctx.noSmooth,
        'pushMatrix': ctx.pushMatrix,
        'popMatrix': ctx.popMatrix,
        'translate': ctx.translate,
        'rotate': ctx.rotate,
        'radians': radians,
        'createFont': ctx.createFont,
        'textAlign': ctx.textAlign,
        'textFont': textFont_,
        'textSize': textSize_,
        'textLeading': textLeading_,
        'text': ctx.text,
        'cos': cos,
        'sin': sin,
        'lerp': lerp,
        'dist': dist,
        'CLOSE': ctx.CLOSE,
        'P2D': ctx.P2D,
        'P3D': ctx.P3D,
        'LEFT': ctx.LEFT,
        'CENTER': ctx.CENTER,
        'RIGHT': ctx.RIGHT,
        'TOP': ctx.TOP,
        'BOTTOM': ctx.BOTTOM,
        'BASELINE': ctx.BASELINE,
        'PI': math.pi,
    }
    return functions
