import os
import re

import setuptools

with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()

with open('requirements.txt') as file:
    INSTALL_REQUIRES = file.read().splitlines()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'slate/__init__.py'))) as f:
    VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)


classifiers = [
    'Development Status :: 3 - Alpha',
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

project_urls = {
    'Documentation': 'https://github.com/Axelancerr/Slate',
    'Source': 'https://github.com/Axelancerr/Slate',
    'Issue Tracker': 'https://github.com/Axelancerr/Slate/issues',
}

setuptools.setup(
    name='Slate',
    version=VERSION,
    description='A Lavalink and Andesite wrapper.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Axelancerr',
    author_email=None,
    url='https://github.com/Axelancerr/Slate',
    packages=['slate'],
    classifiers=classifiers,
    license='MIT',
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.8",
    project_urls=project_urls,
)
