from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
import indexfile

setup(
    name='IndexFile',
    version=indexfile.__version__,
    description='Index Files API',
    author='Emilio Palumbo',
    url='https://',
    license="GNU General Public License (GPL)",
    long_description='''A set of function to import, manage, export index files data.
''',
    platforms=['lx64'],
    packages=['indexfile'],
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
                      "clint==0.3.1"],
    entry_points={
        'console_scripts': [
            'idxtools = indexfile.commands:main',
        ]
    },
)
