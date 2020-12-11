#! /usr/bin/env python3

class PluginFailure:
    def __init__(self, plugin: str, exception: Exception):
        self.plugin = plugin
        self.reason = str(exception)
        self.exception_type = exception.__class__ or type(exception)

    def __str__(self) -> str:
        return f'Plugin={self.plugin},Reason={self.reason}, Type={self.exception_type}'


class SqapiPluginExecutionError(Exception):
    def __init__(self, failures: list(), *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.failures = failures
