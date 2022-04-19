from ast import List
from copy import deepcopy
import inspect
import io
import os
import pathlib
import typing
from typing import Union, Optional, Dict
import yaml as yaml_lib


def _load_yaml(yaml) -> dict:
    if isinstance(yaml, (str, pathlib.Path, bytes, os.PathLike)):
        with open(yaml) as f:
            return yaml_lib.load(f, yaml_lib.FullLoader)
    else:
        return yaml_lib.load(yaml, yaml_lib.FullLoader)


def load_from_yaml(arg0=None, custom_parse: Optional[Dict] = None):
    """
    Adds the following functions to a class based on annotations
    - `from_dict`
    - `from_yaml_file`
    - `from_multi_conf_yaml_file`

    ## Parameters
    - `custom_parse`: Dictionary with parameter names as keys and callables as values, which allows custom parsing
    """

    if custom_parse is None:
        custom_parse = dict()

    if inspect.isfunction(arg0):
        raise ValueError(f"{arg0} is a function, expected a class")

    def decorator(cls):

        cls_dict: dict = cls.__dict__

        annotations: dict = cls_dict["__annotations__"]
        non_default_params = {k for k in annotations.keys() if k not in cls_dict.keys()}
        default_params = {
            k: cls_dict[k] for k in annotations.keys() if k in cls_dict.keys()
        }

        def _parse(k, v):
            if k in custom_parse.keys():
                return custom_parse[k](v)

            return v

        def from_dict(d: dict) -> cls:
            instance = cls.__new__(cls)

            for p in non_default_params:
                assert p in d.keys(), f"Missing key in dictionary: {p}"
                v = _parse(p, d[p])
                setattr(instance, p, v)
                # instance.__dict__[p] = v
                # instance.p = v

            for p in default_params.keys():
                v = d.get(p, None)
                if v is None:
                    v = default_params[p]
                else:
                    v = _parse(p, v)
                setattr(instance, p, v)
                # instance.__dict__[p] = v
                # instance.p = v

            return instance

        def from_yaml_file(yaml: Union[str, typing.TextIO, typing.BinaryIO]) -> cls:
            return from_dict(_load_yaml(yaml))

        def from_multi_conf_yaml_file(
            yaml: Union[str, typing.TextIO, typing.BinaryIO]
        ) -> cls:
            """
            The format:
            Object `base`: default experiment configuration, containing all hyperparameters
            List `deltas`: List of changes in hyperparameters compared to base, all deltas result in a new configuration

            ## params
            - `yaml_file`: file containing the configuration

            ## returns
            A list of experiment configurations, the first of which is the base config
            """

            multi_conf = _load_yaml(yaml)

            base_dict: dict = multi_conf["base"]
            result = [from_dict(base_dict)]

            if "deltas" not in multi_conf.keys():
                return result

            deltas: List[dict] = multi_conf["deltas"]
            for delta in deltas:
                delta_dict = deepcopy(base_dict)
                delta_dict.update(delta)
                result.append(from_dict(delta_dict))

            return result

        setattr(cls, "from_dict", staticmethod(from_dict))
        setattr(cls, "from_yaml_file", staticmethod(from_yaml_file))
        setattr(
            cls, "from_multi_conf_yaml_file", staticmethod(from_multi_conf_yaml_file)
        )

        return cls

    if inspect.isclass(arg0):
        return decorator(arg0)

    return decorator
