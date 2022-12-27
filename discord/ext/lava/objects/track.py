from typing import Generic, TypeVar, TypedDict, cast

from ..types.objects.track import TrackData


__all__: list[str] = ["Track"]

TrackExtrasT = TypeVar("TrackExtrasT", bound=TypedDict, default=TypedDict)


class Track(Generic[TrackExtrasT]):

    __slots__ = (
        "encoded", "identifier", "_is_seekable", "author", "length", "_is_stream",
        "position", "title", "uri", "artwork_url", "isrc", "source_name", "extras"
    )

    def __init__(self, data: TrackData, extras: TrackExtrasT | None = None) -> None:
        self.encoded: str = data["encoded"]

        info = data["info"]
        self.identifier: str = info["identifier"]
        self.author: str = info["author"]
        self.length: int = info["length"]
        self.position: int = info["position"]
        self.title: str = info["title"]
        self.uri: str | None = info["uri"]
        self.artwork_url: str | None = info["artworkUrl"]
        self.isrc: str | None = info["isrc"]
        self.source_name: str = info["sourceName"]

        self._is_seekable: bool = info["isSeekable"]
        self._is_stream: bool = info["isStream"]

        self.extras: TrackExtrasT = extras or cast(TrackExtrasT, {})

    def __repr__(self) -> str:
        return f"discord.ext.lava.Track identifier='{self.identifier}', title='{self.title}', author='{self.author}', length={self.length}>"

    def is_seekable(self) -> bool:
        return self._is_seekable

    def is_stream(self) -> bool:
        return self._is_stream
