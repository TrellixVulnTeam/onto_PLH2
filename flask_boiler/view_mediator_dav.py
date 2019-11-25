import time

from flask_boiler.context import Context as CTX
from flasgger import SwaggerView
from flask import request

from google.cloud.firestore import Watch, DocumentSnapshot, \
    DocumentReference, Query

from flask_boiler.domain_model import DomainModel


class ViewMediatorDAV:
    """
    Watches and updates Firestore for DocumentAsView view models
    """

    def __init__(self,
                 view_model_cls=None,
                 mutation_cls=None):
        """

        :param view_model_cls: the view model to be exposed in REST API
        :param app: Flask App
        :param mutation_cls: a subclass of Mutation to handle the changes
                POST, PATCH, UPDATE, PUT, DELETE made to the list of view
                models or a single view model.
        """
        self.view_model_cls = view_model_cls
        self.mutation_cls = mutation_cls
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
        obj.save()

    def _get_collection_name(self):
        return self.view_model_cls.__name__

    def _get_patch_query(self) -> Query:
        collection_group_id = "_PATCH_{}" \
            .format(self._get_collection_name())
        collection_group_query = CTX.db.collection_group(collection_group_id)
        return collection_group_query

    def _listen_to_patch(self):
        # NOTE: index for subcollection group may need to be created
        #   See: https://firebase.google.com/docs/firestore/query-data/queries#top_of_page

        def on_snapshot(snapshots, changes, timestamp):
            for doc in snapshots:
                # doc: DocumentSnapshot = snapshots[0]
                data = doc.to_dict()
                data = {
                    self.view_model_cls.get_schema_cls().g(key): val
                    for key, val in data.items()
                }

                # ie. doc from /UserViewDAV/user_id_a/_PATCH_UserViewDAV/patch_id_1
                parent_view_ref: DocumentReference = doc.reference.parent.parent
                obj = self.instances[parent_view_ref._document_path]

                self.mutation_cls.mutate_patch_one(obj=obj, data=data)

        watch = Watch.for_query(
            query=self._get_patch_query(),
            snapshot_callback=on_snapshot,
            snapshot_class_instance=DocumentSnapshot,
            reference_class_instance=DocumentReference)

    def start(self):
        """ Generates view models and listen to changes proposed to
                the view model.
        """
        self.instances = self.generate_entries()
        # time.sleep(3)  # TODO: delete after implementing sync
        self._listen_to_patch()

    def generate_entries(self):
        raise NotImplementedError
