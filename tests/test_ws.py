"""
Tests Websocket integration

"""

import pytest
from unittest.mock import MagicMock, patch
from flask_boiler.view_mediator_websocket import ViewMediatorWebsocket
from .color_fixtures import Color, PaletteViewModel, rainbow_vm, color_refs
from .fixtures import setup_app, CTX
import flask_socketio
import time


def test_connect(setup_app, rainbow_vm, color_refs):
    app = setup_app

    class Demo(ViewMediatorWebsocket):
        pass

    mediator = Demo(view_model_cls=rainbow_vm,
                    mutation_cls=None,
                    namespace="/palette")

    io = flask_socketio.SocketIO(app=app)

    io.on_namespace(mediator)

    client = io.test_client(app=app, namespace='/palette')

    assert client.is_connected(namespace='/palette') is True

    res = client.emit('subscribe_view_model',
                      {"color_names": "cian+magenta+yellow"},
                      namespace='/palette')

    assert client.get_received(namespace="/palette") == \
           [{'args': 'connected', 'name': 'message', 'namespace': '/palette'},
            {'args': '{}', 'name': 'message', 'namespace': '/palette'},
            {'args': '{}', 'name': 'message', 'namespace': '/palette'},
            {'args': [None], 'name': 'subscribed', 'namespace': '/palette'},
            {'args': [{'colors': ['cian', 'magenta', 'yellow'],
                       'rainbowName': 'cian-magenta-yellow'}],
             'name': 'updated',
             'namespace': '/palette'}]
