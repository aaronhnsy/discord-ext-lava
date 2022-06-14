Installing
==========

Requirements
------------
Slate requires Python 3.10+. You can download the latest version of python `here <https://www.python.org/downloads/>`__

* `aiohttp <https://pypi.org/project/aiohttp/>`_
* `typing_extensions <https://pypi.org/project/typing_extensions/>`_
* `spoti.py <https://pypi.org/project/spoti.py/>`_

.. admonition:: Note
    :class: note

    You don't have to install the packages manually as they will be installed automatically with pip. Just ensure you have python setup and pip added to path.
.. admonition:: Caution
    :class: caution

    Make sure you have Installed & Setup git before proceeding. You can install it `here <https://git-scm.com/>`__

Installing Stable Version
-------------------------
This installs the latest stable release of slate from github

.. tab:: Windows

    .. code-block:: console

        py -3 -m pip install -U git+https://github.com/Axelware/slate.git@v0.3.1
.. tab:: MacOS/Linux

    .. code-block:: console

        python3 -m pip install -U git+https://github.com/Axelware/slate.git@v0.3.1

Installing Development Version
-------------------------------
This installs the master branch from github

.. admonition:: Warning
    :class: attention

    Installing the development version is not recommended as it may contain bugs.

.. tab:: Windows

    .. code-block:: console

        py -3 -m pip install -U git+https://github.com/Axelware/slate.git
.. tab:: MacOS/Linux

    .. code-block:: console

        python3 -m pip install -U git+https://github.com/Axelware/slate.git
