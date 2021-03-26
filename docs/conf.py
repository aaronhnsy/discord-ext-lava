# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('extensions'))

# -- Project information -----------------------------------------------------

project = 'slate.py'
author = 'Axel#3456'
copyright = '2020 - Axel#3456'
version = '0.1.0'
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

needs_sphinx = '3.4.0'

extensions = [
    'faculty_sphinx_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinxcontrib_trio',
    'resourcelinks'
]

napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True  # TODO maybe change this

autodoc_typehints = 'signature'
autodoc_member_order = 'bysource'

extlinks = {
    'issue': ('https://github.com/Axelancerr/Slate/issues/%s', 'GH-'),
}

intersphinx_mapping = {
    'py':      ('https://docs.python.org/3.9', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable/', None),
    'dpy':     ('https://discordpy.readthedocs.io/en/latest/', None)
}

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'faculty-sphinx-theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_experimental_html5_writer = True

html_context = {
    'discord_invite': 'https://discord.gg/r3sSKJJ',
}

resource_links = {
    'discord':     'https://discord.gg/xP8xsHr',
    'issues':      'https://github.com/Axelancerr/Slate/issues',
    'discussions': 'https://github.com/Axelancerr/Slate/discussions',
    'andesite':    'https://github.com/natanbc/andesite',
    'lavalink':    'https://github.com/Frederikam/Lavalink'
}
