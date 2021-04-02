import os
import sys
import re

sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('extensions'))

project = 'slate.py'
copyright = '2020-Present, Axel#3456'
author = 'Axel#3456'

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../slate/__init__.py'))) as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)
    release = version

needs_sphinx = '3.5.2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinxcontrib_trio',
    'resourcelinks',
    'faculty_sphinx_theme',
]

napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True

autodoc_typehints = 'description'
autodoc_member_order = 'bysource'

extlinks = {
    'issue': ('https://github.com/Axelancerr/Slate/issues/%s', 'GH-'),
}

intersphinx_mapping = {
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "python": ("https://docs.python.org/3.9", None),
    "discord": ("https://discordpy.readthedocs.io/en/latest", None),
}

html_theme = 'faculty-sphinx-theme'
highlight_language = "python3"
master_doc = "index"
pygments_style = "friendly"
source_suffix = ".rst"

resource_links = {
    'issues':      'https://github.com/Axelancerr/Slate/issues',
    'discussions': 'https://github.com/Axelancerr/Slate/discussions',
    'andesite':    'https://github.com/natanbc/andesite',
    'lavalink':    'https://github.com/Frederikam/Lavalink'
}
