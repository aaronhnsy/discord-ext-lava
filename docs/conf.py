# Future
from __future__ import annotations

# Standard Library
import os
import re
import sys


# Project information
project = "slate"
author = "Axel#3456"
copyright = "2020-present - Axelancerr"

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../slate/__init__.py'))) as file:
    version = re.search(r"^__version__: [^=]* = \"([^\"]*)\"", file.read(), re.MULTILINE).group(1)
    release = version

# General configuration
sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinxcontrib_trio",
    "resourcelinks",
]

needs_sphinx = "3.5.2"

# Options for HTML output
html_theme = "furo"

# Other settings
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True

autodoc_typehints = "description"
autodoc_member_order = "bysource"

extlinks = {
    "issue": ("https://github.com/Axelware/slate/issues/%s", "GH-"),
}

intersphinx_mapping = {
    'aiohttp': ('https://docs.aiohttp.org/en/stable/', None),
    'python':  ('https://docs.python.org/3.10', None),
    'discord': ('https://discordpy.readthedocs.io/en/latest', None),
}

resource_links = {
    "github":      "https://github.com/Axelware/slate",
    "issues":      "https://github.com/Axelware/slate/issues",
    "discussions": "https://github.com/Axelware/slate/discussions",

    "examples":    "https://github.com/Axelware/slate/tree/main/examples",

    "discord.py":  "https://github.com/Rapptz/discord.py",
    "lavalink":    "https://github.com/freyacodes/Lavalink",
    "obsidian":    "https://github.com/mixtape-bot/obsidian/tree/v2",

    "discord":     "https://discord.com/invite/w9f6NkQbde",

}
