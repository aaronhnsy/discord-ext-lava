# Future
from __future__ import annotations

# Standard Library
import os
import re
import sys
from typing import Any


_DISCORD: str = "https://discord.com/invite/w9f6NkQbde"
_DISCORD_SVG: str = """
<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
    <path d="M6.552 6.712c-.456 0-.816.4-.816.888s.368.888.816.888c.456 0 .816-.4.816-.888.008-.488-.36-.888-.816-.888zm2.92 0c-.456 0-.816.4-.816.888s.368.888.816.888c.456 0 .816-.4.816-.888s-.36-.888-.816-.888z"></path>
    <path d="M13.36 0H2.64C1.736 0 1 .736 1 1.648v10.816c0 .912.736 1.648 1.64 1.648h9.072l-.424-1.48 1.024.952.968.896L15 16V1.648C15 .736 14.264 0 13.36 0zm-3.088 10.448s-.288-.344-.528-.648c1.048-.296 1.448-.952 1.448-.952-.328.216-.64.368-.92.472-.4.168-.784.28-1.16.344a5.604 5.604 0 0 1-2.072-.008 6.716 6.716 0 0 1-1.176-.344 4.688 4.688 0 0 1-.584-.272c-.024-.016-.048-.024-.072-.04-.016-.008-.024-.016-.032-.024-.144-.08-.224-.136-.224-.136s.384.64 1.4.944c-.24.304-.536.664-.536.664-1.768-.056-2.44-1.216-2.44-1.216 0-2.576 1.152-4.664 1.152-4.664 1.152-.864 2.248-.84 2.248-.84l.08.096c-1.44.416-2.104 1.048-2.104 1.048s.176-.096.472-.232c.856-.376 1.536-.48 1.816-.504.048-.008.088-.016.136-.016a6.521 6.521 0 0 1 4.024.752s-.632-.6-1.992-1.016l.112-.128s1.096-.024 2.248.84c0 0 1.152 2.088 1.152 4.664 0 0-.68 1.16-2.448 1.216z"></path>
</svg>
"""

_GITHUB: str = "https://github.com/Axelware/slate"
_GITHUB_SVG: str = """
<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
</svg>
"""


#######################
# Project Information #
#######################

project: str = "slate"
copyright: str = "2020 - Present, Aaron Hennessey"
author: str = "Aaron Hennessey"

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../slate/__init__.py"))) as file:

    if not (match := re.search(r"^__version__: [^=]* = \"([^\"]*)\"", file.read(), re.MULTILINE)):
        raise RuntimeError

    _VERSION: str = match[1]
    version: str = _VERSION
    release: str = _VERSION


#########################
# General Configuration #
#########################

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))

extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinxcontrib_trio",
    "resource_links",
    "sphinx_copybutton",
    "sphinx_inline_tabs"
]
exclude_patters: list[str] = [
    "_build",
    "Thumbs.db",
    ".DS_Store"
]

needs_sphinx: str = "4.5.0"
nitpicky: bool = True


###########################
# Options for HTML output #
###########################

html_theme: str = "furo"

html_theme_options: dict[str, Any] = {
    "footer_icons": [
        {
            "name":  "Discord",
            "url":   _DISCORD,
            "html":  _DISCORD_SVG,
            "class": "",
        },
        {
            "name":  "GitHub",
            "url":   _GITHUB,
            "html":  _GITHUB_SVG,
            "class": "",
        },
    ],
}
html_title: str = "slate"

html_css_files: list[str] = [
    "custom.css",
]
html_static_path: list[str] = [
    "static"
]


##############
# Extensions #
##############

# autodoc
autoclass_content: str = "class"
autodoc_class_signature: str = "mixed"
autodoc_member_order: str = "bysource"
autodoc_default_options: dict[str, Any] = {
    "undoc-members": True
}
autodoc_typehints: str = "signature"
autodoc_type_aliases: dict[str, str] = {
    "BotT": "discord.ext.commands.Bot | discord.ext.commands.AutoShardedBot",
    "ContextT": "~discord.ext.commands.Context",
    "PlayerT": "~slate.Player",
}
autodoc_typehints_format: str = "short"


# napoleon
napoleon_use_admonition_for_examples: bool = True
napoleon_use_admonition_for_notes: bool = True


# intersphinx
intersphinx_mapping: dict[str, tuple[str, None]] = {
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "python":  ("https://docs.python.org/3.10", None),
    "discord": ("https://discordpy.readthedocs.io/en/latest", None),
}


# ext links
extlinks: dict[str, tuple[str, str]] = {
    "issue": (f"{_GITHUB}/issues/%s", "GH-"),
}
extlinks_detect_hardcoded_links: bool = True


# resource links
resource_links: dict[str, str] = {
    "github":      _GITHUB,
    "issues":      f"{_GITHUB}/issues",
    "discussions": f"{_GITHUB}/discussions",

    "examples":    f"{_GITHUB}/tree/main/examples",

    "discord":     _DISCORD,

    "discord.py":  "https://github.com/Rapptz/discord.py",
    "lavalink":    "https://github.com/freyacodes/Lavalink",
    "obsidian":    "https://github.com/mixtape-bot/obsidian/tree/v2",
}
