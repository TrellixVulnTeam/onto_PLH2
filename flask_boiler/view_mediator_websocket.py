import time

from flask_boiler.context import Context as CTX
from flasgger import SwaggerView
from flask import request

from google.cloud.firestore import Watch, DocumentSnapshot, \
    DocumentReference, Query

from flask_boiler.domain_model import DomainModel
from flask_boiler.view_mediator import ViewMediatorBase

from flask_socketio import Namespace, emit, send

from functools import partial

import json


class ViewMediatorWebsocket(ViewMediatorBase, Namespace):
    """
    Watches and updates Firestore for DocumentAsView view models
    """

    def __init__(self,
                 view_model_cls=None,
                 mutation_cls=None, *args, **kwargs):
        """

        :param view_model_cls: the view model to be exposed in REST API
        :param app: Flask App
        :param mutation_cls: a subclass of Mutation to handle the changes
                POST, PATCH, UPDATE, PUT, DELETE made to the list of view
                models or a single view model.
        """
        super().__init__(view_model_cls=view_model_cls,
                         mutation_cls=mutation_cls, *args, **kwargs)
        self.rule_view_cls_mapping = dict()
        self.default_tag = self.view_model_cls.__name__
        self.instances = dict()

    @classmethod
    def notify(cls, obj):
        """ Specifies what to do with the view model newly generated
                from an update.

        :param obj:
        :return:
        """
        pass

    def on_connect(self):
        """
        Ref: https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/test_socketio.py
        :return:
        """
        if request.args.get('fail'):
            return False
        send('connected')
        send(json.dumps(request.args.to_dict(flat=False)))
        send(json.dumps({h: request.headers[h] for h in request.headers.keys()
                         if
                         h not in ['Host', 'Content-Type', 'Content-Length']}))

    def on_disconnect(self):
        pass

    def on_subscribe_view_model(self, data):
        self.instances[0] = self.view_model_cls.new(
            **data,
            once=False,
            f_notify=self.notify
        )
        emit("subscribed")
        time.sleep(5)
        emit("updated", self.instances[0].to_view_dict())
