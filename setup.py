try:
    from setuptools import setup, Extension
except:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Extension

import indexfile

setup(
    name=indexfile.__name__,
    version=indexfile.__version__,
    description='Indexfile API and tools',
    author='Emilio Palumbo',
    url='https://github.com/emi80/idxtools',
    license="GNU General Public License (GPL)",
    long_description=open('README.rst').read(),
    platforms=['lx64'],
    packages=['indexfile','indexfile.cli'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    install_requires=["argparse==1.2.1",
                      "clint==0.3.1",
                      "docopt==0.6.1",
                      "simplejson==3.3.2",
                      "lockfile==0.9.1"],
    entry_points={
        'console_scripts': [
            '%s = indexfile.cli.indexfile_main:main' % indexfile.__name__,
        ]
    },
)
