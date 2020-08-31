#! /usr/bin/env python3
import abc


class SqapiConfiguration:
    class EdgeConfig:
        def __init__(self):
            pass

    class MessageConfig:
        def __init__(self, **kwargs):
            broker              = kwargs.get('broker') or         {}      # Message specific
            message             = kwargs.get('message') or        {}      # Message specific

    class PluginConfig:
        def __init__(self, **kwargs):
            plugin              = kwargs.get('plugin') or         {}      # Plugin specific
            custom              = kwargs.get('custom') or         {}      # Plugin specific

    class StorageConfig:
        def __init__(self, **kwargs):
            database            = kwargs.get('database') or       {}      # Storage specific
            meta_store          = kwargs.get('meta_store') or     {}      # Storage specific
            data_store          = kwargs.get('data_store') or     {}      # Storage specific

    class DependencyConfig:
        def __init__(self, **kwargs):
            packages            = kwargs.get('packages') or       {}      # Dependencies


class SqapiMessenger():
    def __init__(self):
        config = SqapiConfiguration()
        broker = Broker()


class SqapiPluginManager:
    def __init__(self):
        config = SqapiConfiguration()


class SqapiProcessManager:
    def __init__(self):
        config = SqapiConfiguration()


class SqapiResourceManager:
    def __init__(self):
        config = SqapiConfiguration()


class SqapiApplication:

    def __init__(self):
        config = SqapiConfiguration()
        self.messenger = SqapiMessenger()

        self.plugin_manager = SqapiPluginManager()
        self.process_manager = SqapiProcessManager()
        self.resource_manager = SqapiResourceManager()


if __name__ == '__main__':
    broker = Broker()
    broker.start()
    broker.listen()
