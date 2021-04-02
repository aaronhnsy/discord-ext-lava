import os
import re

import setuptools

with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()

with open('requirements.txt') as file:
    INSTALL_REQUIRES = file.read().splitlines()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'slate/__init__.py'))) as f:
    VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: AsyncIO',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Typing :: Typed'
]

PROJECT_URLS = {
    'Documentation': 'https://slate-py.readthedocs.io/en/latest/',
    'Source': 'https://github.com/Axelancerr/Slate',
    'Issue Tracker': 'https://github.com/Axelancerr/Slate/issues',
}


EXTRAS_REQUIRE = {
    'docs': [
        'sphinx',
        'sphinxcontrib_trio',
        'faculty-sphinx-theme',
    ],
}

setuptools.setup(
    author='Axelancerr',
    classifiers=CLASSIFIERS,
    description='A Lavalink and Andesite wrapper.',
    extras_require=EXTRAS_REQUIRE,
    install_requires=INSTALL_REQUIRES,
    license='MIT',
    name='Slate',
    packages=['slate', 'slate.andesite', 'slate.lavalink', 'slate.bases', 'slate.objects'],
    project_urls=PROJECT_URLS,
    python_requires=">=3.8",
    url='https://github.com/Axelancerr/Slate',
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
)
