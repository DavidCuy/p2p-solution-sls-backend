# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Reverter(ABC):
    @abstractmethod
    def set_next(self, handler: Reverter) -> Reverter:
        pass

    @abstractmethod
    def revert(self, request):
        pass


class AbstractReverter(Reverter):
    _next_handler = None

    def set_next(self, reverter: Reverter) -> Reverter:
        self._next_handler = reverter
        return reverter

    @abstractmethod
    def revert(self, request: Any):
        if self._next_handler:
            return self._next_handler.revert(request)

        return None
