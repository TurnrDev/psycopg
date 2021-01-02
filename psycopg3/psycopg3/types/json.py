"""
Adapers for JSON types.
"""

# Copyright (C) 2020 The Psycopg Team

import json
from typing import Any, Callable, Optional

from ..oids import builtins
from ..adapt import Dumper, Loader, Format
from ..errors import DataError

JsonDumpsFunction = Callable[[Any], str]


class _JsonWrapper:
    def __init__(self, obj: Any, dumps: Optional[JsonDumpsFunction] = None):
        self.obj = obj
        self._dumps: JsonDumpsFunction = dumps or json.dumps

    def dumps(self) -> str:
        return self._dumps(self.obj)


class Json(_JsonWrapper):
    pass


class Jsonb(_JsonWrapper):
    pass


class _JsonDumper(Dumper):

    format = Format.TEXT

    def dump(self, obj: _JsonWrapper) -> bytes:
        return obj.dumps().encode("utf-8")


class JsonDumper(_JsonDumper):

    format = Format.TEXT
    _oid = builtins["json"].oid


class JsonBinaryDumper(JsonDumper):

    format = Format.BINARY


class JsonbDumper(_JsonDumper):

    format = Format.TEXT
    _oid = builtins["jsonb"].oid


class JsonbBinaryDumper(JsonbDumper):

    format = Format.BINARY

    def dump(self, obj: _JsonWrapper) -> bytes:
        return b"\x01" + obj.dumps().encode("utf-8")


class JsonLoader(Loader):

    format = Format.TEXT

    def load(self, data: bytes) -> Any:
        return json.loads(data)


class JsonBinaryLoader(JsonLoader):

    format = Format.BINARY


class JsonbBinaryLoader(Loader):

    format = Format.BINARY

    def load(self, data: bytes) -> Any:
        if data and data[0] != 1:
            raise DataError("unknown jsonb binary format: {data[0]}")
        return json.loads(data[1:])
