.. py:currentmodule:: discord.ext.lava


Reference
=========

Pool
----
.. autoclass:: Pool
    :members:

Node
----
.. autoclass:: discord.ext.lava.Node
    :members:

Player
------
.. autoclass:: discord.ext.lava.Player
    :members:
    :exclude-members: on_voice_server_update, on_voice_state_update

Queue
-----
.. autoclass:: discord.ext.lava.Queue
    :members:


Objects
-------

Track
~~~~~
.. autoclass:: discord.ext.lava.Track
    :members:

Collection
~~~~~~~~~~
.. autoclass:: discord.ext.lava.Collection
    :members:

Search
~~~~~~
.. autoclass:: discord.ext.lava.Search
    :members:


Events
------

TrackStart
~~~~~~~~~~
.. autoclass:: discord.ext.lava.TrackStart
    :members:

TrackEnd
~~~~~~~~
.. autoclass:: discord.ext.lava.TrackEnd
    :members:

TrackStuck
~~~~~~~~~~
.. autoclass:: discord.ext.lava.TrackStuck
    :members:

TrackException
~~~~~~~~~~~~~~
.. autoclass:: discord.ext.lava.TrackException
    :members:

WebsocketOpen
~~~~~~~~~~~~~
.. autoclass:: discord.ext.lava.WebsocketOpen
    :members:

WebsocketClosed
~~~~~~~~~~~~~~~
.. autoclass:: discord.ext.lava.WebsocketClosed
    :members:


Filters
-------

ChannelMix
~~~~~~~~~~
.. autoclass:: discord.ext.lava.ChannelMix
    :members:

Distortion
~~~~~~~~~~
.. autoclass:: discord.ext.lava.Distortion
    :members:

Equalizer
~~~~~~~~~
.. autoclass:: discord.ext.lava.Equalizer
    :members:

Karaoke
~~~~~~~
.. autoclass:: discord.ext.lava.Karaoke
    :members:

LowPass
~~~~~~~
.. autoclass:: discord.ext.lava.LowPass
    :members:

Rotation
~~~~~~~~
.. autoclass:: discord.ext.lava.Rotation
    :members:

Timescale
~~~~~~~~~
.. autoclass:: discord.ext.lava.Timescale
    :members:

Tremolo
~~~~~~~
.. autoclass:: discord.ext.lava.Tremolo
    :members:

Vibrato
~~~~~~~
.. autoclass:: discord.ext.lava.Vibrato
    :members:

Volume
~~~~~~
.. autoclass:: discord.ext.lava.Volume
    :members:

Filter
~~~~~~
.. autoclass:: discord.ext.lava.Filter
    :members:


Enums
-----

Provider
~~~~~~~~
.. autoclass:: discord.ext.lava.Provider
    :members:

QueueLoopMode
~~~~~~~~~~~~~
.. autoclass:: discord.ext.lava.QueueLoopMode
    :members:

Source
~~~~~~
.. autoclass:: discord.ext.lava.Source
    :members:


Exceptions
----------

LavaError
~~~~~~~~~~
.. autoexception:: discord.ext.lava.LavaError

NodeAlreadyExists
~~~~~~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.NodeAlreadyExists

NodeNotFound
~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.NodeNotFound

NoNodesConnected
~~~~~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.NoNodesConnected

NodeAlreadyConnected
~~~~~~~~~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.NodeAlreadyConnected

NodeConnectionError
~~~~~~~~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.NodeConnectionError

InvalidPassword
~~~~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.InvalidPassword

NodeNotConnected
~~~~~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.NodeNotConnected

HTTPError
~~~~~~~~~
.. autoexception:: discord.ext.lava.HTTPError
   :members:

NoResultsFound
~~~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.NoResultsFound
   :members:

SearchFailed
~~~~~~~~~~~~
.. autoexception:: discord.ext.lava.SearchFailed
   :members:


Utils
-----

SPOTIFY_URL_REGEX
~~~~~~~~~~~~~~~~~
.. attribute:: discord.ext.lava.SPOTIFY_URL_REGEX

A regex that matches spotify URLs for tracks, albums, playlists, and artists.


MISSING
~~~~~~~
.. attribute:: discord.ext.lava.MISSING

A sentinel value that is used to indicate a missing value with distinction from :class:`None`.
