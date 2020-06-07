from distutils.core import setup

setup(
    name='jupyter-processing-pymatplotlib',
    version='0.1dev',
    packages=['processingpymat',],
    license='MIT license',
    long_description=open('README.md').read(),
    install_requires=[
        'matplotlib',
    ],
)
