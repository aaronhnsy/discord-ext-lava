.. py:currentmodule:: slate


API Reference
=============

Node
----
.. autoclass:: slate.Node
    :members:

Player
------
.. autoclass:: slate.Player
    :members:

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

BaseFilter
~~~~~~~~~~
.. autoclass:: slate.BaseFilter
    :members:

Tremolo
~~~~~~~
.. autoclass:: slate.Tremolo
    :members:

Equalizer
~~~~~~~~~
.. autoclass:: slate.Equalizer
    :members:

Distortion
~~~~~~~~~~
.. autoclass:: slate.Distortion
    :members:

Timescale
~~~~~~~~~
.. autoclass:: slate.Timescale
    :members:

Karaoke
~~~~~~~
.. autoclass:: slate.Karaoke
    :members:

ChannelMix
~~~~~~~~~~
.. autoclass:: slate.ChannelMix
    :members:

Vibrato
~~~~~~~
.. autoclass:: slate.Vibrato
    :members:

Rotation
~~~~~~~~
.. autoclass:: slate.Rotation
    :members:

LowPass
~~~~~~~
.. autoclass:: slate.LowPass
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
