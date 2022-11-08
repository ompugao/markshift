# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class Renderer(metaclass=ABCMeta):
    def __init__(self, ):
        pass

    @abstractmethod
    def render(self, elem):
        raise NotImplementedError()

    @abstractmethod
    def render_strong(self, elem):
        raise NotImplementedError()

    @abstractmethod
    def render_italic(self, elem):
        raise NotImplementedError()

    @abstractmethod
    def render_raw(self, elem):
        raise NotImplementedError()

    @abstractmethod
    def render_quote(self, elem):
        raise NotImplementedError()

    @abstractmethod
    def render_code(self, elem):
        raise NotImplementedError()

    @abstractmethod
    def render_math(self, elem):
        raise NotImplementedError()
