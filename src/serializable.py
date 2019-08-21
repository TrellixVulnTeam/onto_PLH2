import warnings

from marshmallow import MarshalResult

from .schema import generate_schema


class Serializable(object):

    _fields = None
    _schema_cls = None
    _schema_obj = None

    _registry = dict()  # classname: cls

    @property
    def schema_obj(self):
        if self._schema_obj is None:
            self._schema_obj = self._schema_cls()
        return self._schema_obj

    @property
    def schema_cls(self):
        return self._schema_cls

    @classmethod
    def get_schema_cls(cls):
        return cls._schema_cls

    def __init_subclass__(cls, serializable_fields=None, **kwargs):
        """
        See: https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__
        :param serializable_fields:
        :param kwargs:
        :return:
        """
        super().__init_subclass__(**kwargs)
        cls._registry[cls.__name__] = cls
        cls._fields = serializable_fields
        # if cls._schema is None:
        #     cls._schema = generate_schema(cls)

    @classmethod
    def get_subclass_cls(cls, obj_type):
        """ Returns cls from obj_type (classname string)
        obj_type must be a subclass of cls in current class/object
        """
        if obj_type in cls._registry:
            return cls._registry[obj_type]
        else:
            return None

    @classmethod
    def _infer_fields(cls) -> list:
        res = list()

        def is_private_var_name(var_name):
            if len(var_name) == 0:
                raise ValueError
            else:
                return var_name[0] == "_"

        for key, val in cls.__dict__.items():
            if not is_private_var_name(key):
                if not callable(val):
                    res.append(key)

        return res


    @classmethod
    def get_fields(cls) -> list:
        """
        Returns a list of fields that are serialized and deserialized.

        :return:
        """

        if cls._fields is None:
            warnings.warn("Inferring fields to serialize and deserialize "
                          "by variable name. "
                          "serializable_fields should rather " +
                          "be specified. Eg. " +
                          "class SubclassOfViewModel(" +
                          "ViewModel, serializable_fields=['property_a'])")
            return cls._infer_fields()
        else:
            return cls._fields

    # def __new__(cls, *args, **kwargs):
    #
    #     instance = super().__new__(cls, *args, **kwargs)
    #     return instance

    def _export_as_dict(self) -> dict:
        print(self.schema_obj)
        print(self)
        mres: MarshalResult = self.schema_obj.dump(self)
        return mres.data

    def _import_properties(self, d: dict) -> None:
        deserialized = self.schema_obj.load(d).data
        for key, val in deserialized.items():
            setattr(self, key, val)

    def to_dict(self):
        return self._export_as_dict()

    @classmethod
    def from_dict(cls, d, **kwargs):
        instance = cls(**kwargs)  # TODO: fix unexpected arguments
        instance._import_properties(d)
        return instance
