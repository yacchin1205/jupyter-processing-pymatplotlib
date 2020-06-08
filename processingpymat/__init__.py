from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic, needs_local_scope)
import matplotlib.pyplot as plt
from .processing import Processing


@magics_class
class ProcessingPyMatplotlibMagics(Magics):
    def __init__(self, shell=None, **kwargs):
        super(ProcessingPyMatplotlibMagics, self).__init__(shell=shell, **kwargs)
        self._lastprocess = None

    @line_magic
    def lastprocess(self, line):
        return self._lastprocess

    @cell_magic
    @needs_local_scope
    def processing(self, line, cell, local_ns={}):
        args = dict([tuple(arg_) if len(arg_) == 2 else (arg_[0], True)
                     for arg_ in [arg.split('=') for arg in line.split()]])

        self._lastprocess = Processing(cell, local_ns)

        fig = plt.figure()
        ax = fig.gca()

        kwargs = {}
        for key in ['skipframes', 'frames', 'framerate']:
            if key not in args:
                continue
            kwargs[key] = int(args[key])
        if 'debug' in args:
            kwargs['drawrate'] = args['debug']

        anim = self._lastprocess.plot(fig, ax, **kwargs)
        plt.show()

        return self._lastprocess, anim

def load_ipython_extension(ipython):
    ipython.register_magics(ProcessingPyMatplotlibMagics)
