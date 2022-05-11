.. py:currentmodule:: slate


API Reference
=============

Pool
----
.. autoclass:: Pool
    :members:

Node
----
.. autoclass:: slate.Node
    :members:

Player
------
.. autoclass:: slate.Player
    :members:
    :exclude-members: on_voice_server_update, on_voice_state_update

Queue
-----
.. autoclass:: slate.Queue
    :members:


Objects
-------

Track
~~~~~
.. autoclass:: slate.Track
    :members:

Collection
~~~~~~~~~~
.. autoclass:: slate.Collection
    :members:

Search
~~~~~~
.. autoclass:: slate.Search
    :members:


Events
------

TrackStart
~~~~~~~~~~
.. autoclass:: slate.TrackStart
    :members:

TrackEnd
~~~~~~~~
.. autoclass:: slate.TrackEnd
    :members:

TrackStuck
~~~~~~~~~~
.. autoclass:: slate.TrackStuck
    :members:

TrackException
~~~~~~~~~~~~~~
.. autoclass:: slate.TrackException
    :members:

WebsocketOpen
~~~~~~~~~~~~~
.. autoclass:: slate.WebsocketOpen
    :members:

WebsocketClosed
~~~~~~~~~~~~~~~
.. autoclass:: slate.WebsocketClosed
    :members:


Filters
-------

ChannelMix
~~~~~~~~~~
.. autoclass:: slate.ChannelMix
    :members:

Distortion
~~~~~~~~~~
.. autoclass:: slate.Distortion
    :members:

Equalizer
~~~~~~~~~
.. autoclass:: slate.Equalizer
    :members:

Karaoke
~~~~~~~
.. autoclass:: slate.Karaoke
    :members:

LowPass
~~~~~~~
.. autoclass:: slate.LowPass
    :members:

Rotation
~~~~~~~~
.. autoclass:: slate.Rotation
    :members:

Timescale
~~~~~~~~~
.. autoclass:: slate.Timescale
    :members:

Tremolo
~~~~~~~
.. autoclass:: slate.Tremolo
    :members:

Vibrato
~~~~~~~
.. autoclass:: slate.Vibrato
    :members:

Volume
~~~~~~
.. autoclass:: slate.Volume
    :members:

Filter
~~~~~~
.. autoclass:: slate.Filter
    :members:


Enums
-----

Provider
~~~~~~~~
.. autoclass:: slate.Provider
    :members:

QueueLoopMode
~~~~~~~~~~~~~
.. autoclass:: slate.QueueLoopMode
    :members:

Source
~~~~~~
.. autoclass:: slate.Source
    :members:


Exceptions
----------

SlateError
~~~~~~~~~~
.. autoexception:: slate.SlateError

NodeAlreadyExists
~~~~~~~~~~~~~~~~~
.. autoexception:: slate.NodeAlreadyExists

NodeNotFound
~~~~~~~~~~~~
.. autoexception:: slate.NodeNotFound

NoNodesConnected
~~~~~~~~~~~~~~~~
.. autoexception:: slate.NoNodesConnected

NodeConnectionError
~~~~~~~~~~~~~~~~~~~
.. autoexception:: slate.NodeConnectionError

InvalidNodePassword
~~~~~~~~~~~~~~~~~~~
.. autoexception:: slate.InvalidNodePassword

NodeNotConnected
~~~~~~~~~~~~~~~~
.. autoexception:: slate.NodeNotConnected

HTTPError
~~~~~~~~~
.. autoexception:: slate.HTTPError
   :members:

NoResultsFound
~~~~~~~~~~~~~~
.. autoexception:: slate.NoResultsFound
   :members:

SearchFailed
~~~~~~~~~~~~
.. autoexception:: slate.SearchFailed
   :members:


Utils
-----

SPOTIFY_URL_REGEX
~~~~~~~~~~~~~~~~~
.. attribute:: slate.SPOTIFY_URL_REGEX

A regex that matches spotify URLs for tracks, albums, playlists, and artists.


MISSING
~~~~~~~
.. attribute:: slate.MISSING

A sentinel value that is used to indicate a missing value with distinction from :class:`None`.
