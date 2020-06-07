# jupyter-processing-pymatplotlib [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yacchin1205/jupyter-processing-pymatplotlib/master)


Processing Python Mode on Jupyter Notebook using Matplotlib

This packages provides the `processing` magic which can execute Processing Python Mode scripts on Jupyter Notebook.

## Getting started

To use the package, install this repo by pip.

```
$ pip install git+https://github.com/yacchin1205/jupyter-processing-pymatplotlib.git
```

On your notebook, write and run the script below.

```
%load_ext processingpymat
```

Then you can use `%%processing` magic on the notebook!

```
%%processing
# Example from... https://github.com/Abdur-rahmaanJ/ppython
def setup():
    pass

def draw():
    background(255, 255, 255)
    for i in range(20):
        ry = random(2, 10)*10
        fill(i*10, 100, 20)
        rect(10 + i*10, 150-ry, 10, ry)
        fill(255, 0, 0)
```
