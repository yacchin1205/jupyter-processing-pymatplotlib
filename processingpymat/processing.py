import builtins
from datetime import datetime, timedelta
from .drawing import DrawingContextProxy, DrawingContext, generate_functions
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import HTML


class Processing:

    def __init__(self, cell, local_ns):
        self.cell = cell
        self.local_ns = local_ns

    def plot(self, fig, ax, figsize=(500, 500), frames=60 * 60 * 30, framerate=60, skipframes=0, blit=True, debug=False):
        w, h = figsize
        ax.set_xlim(0, w)
        ax.set_ylim(0, h)
        ax.set_frame_on(False)
        ax.set_xticks([], [])
        ax.set_yticks([], [])
        ax.set_aspect(1)
        gctxproxy = DrawingContextProxy()
        functions = generate_functions(gctxproxy)
        w, h = figsize
        functions['width'] = w
        functions['height'] = h
        for k, f in functions.items():
            setattr(builtins, k, f)

        # setup
        gctx = DrawingContext(fig, ax, figsize=figsize)
        gctxproxy.base = gctx
        ctx = {}
        ctx.update(self.local_ns)
        exec(self.cell, ctx)
        if 'setup' in ctx:
            ctx['setup']()

        ax.invert_yaxis()

        # draw
        def step_animation(frame):
            # Skip frames
            if frame > 0:
                for i in range(skipframes):
                    gctxproxy.base = None
                    startt = datetime.now()
                    gctxproxy.clear()
                    if 'draw' in ctx:
                        ctx['draw']()
                    gctxproxy.flush()
                    durt = (datetime.now() - startt) / timedelta(seconds=1)
                    if debug:
                        print('Draw(frame={}, skipframe={}): duration={} seconds.'.format(frame, i, durt))
            # Draw
            gctxproxy.base = gctx
            startt = datetime.now()
            gctxproxy.clear()
            if 'draw' in ctx:
                ctx['draw']()
            gctxproxy.flush()
            durt = (datetime.now() - startt) / timedelta(seconds=1)
            if debug:
                print('Draw(frame={}): duration={} seconds.'.format(frame, durt))
            return gctx.patches.updates

        # handlers
        if 'keyPressed' in ctx:
            def keyPressed_(event):
                builtins.key = event.key
                ctx['keyPressed']()
            fig.canvas.mpl_connect('key_press_event', keyPressed_)

        if 'keyReleased' in ctx:
            def keyReleased_(event):
                builtins.key = event.key
                ctx['keyReleased']()
            fig.canvas.mpl_connect('key_release_event', keyReleased_)

        return animation.FuncAnimation(fig, step_animation,
                                       frames=frames // (1 + skipframes),
                                       interval=int(1000 / (framerate / (1 + skipframes))),
                                       blit=blit)

    def generate(self, skipframes=0, framerate=60, frames=100, blit=True, debug=False):
        fig = plt.figure()
        ax = fig.gca()
        anim = self.plot(fig, ax, skipframes=skipframes, framerate=framerate , frames=frames, blit=blit, debug=debug)
        return HTML(anim.to_html5_video())
