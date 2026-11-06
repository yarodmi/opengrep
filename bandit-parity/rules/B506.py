import yaml
import yaml as y
from yaml import SafeLoader, CSafeLoader
from yaml import load as load_yaml
import json


def deserialize(stream):
    # ruleid: B506
    yaml.load(stream)
    # ruleid: B506
    y.load(stream)
    # ruleid: B506
    load_yaml(stream)
    # ruleid: B506
    yaml.load(stream, Loader=yaml.Loader)
    # ruleid: B506
    yaml.load(stream, Loader=yaml.UnsafeLoader)
    # ruleid: B506
    yaml.load(stream, yaml.BaseLoader)
    # ruleid: B506
    yaml.load(stream, Loader=yaml.FullLoader)
    # ruleid: B506
    yaml.load(
        stream,
        Loader=yaml.Loader,
    )
    # ok: B506
    yaml.load(stream, Loader=yaml.SafeLoader)
    # ok: B506
    yaml.load(stream, Loader=yaml.CSafeLoader)
    # ok: B506
    yaml.load(stream, Loader=SafeLoader)
    # ok: B506
    yaml.load(stream, Loader=CSafeLoader)
    # ok: B506
    yaml.load(stream, yaml.SafeLoader)
    # ok: B506
    yaml.load(stream, yaml.CSafeLoader)
    # ok: B506
    yaml.load(stream, SafeLoader)
    # ok: B506
    yaml.load(stream, CSafeLoader)
    # B506 only tests load, even if other APIs may also be unsafe.
    # ok: B506
    yaml.load_all(stream)
    # ok: B506
    yaml.unsafe_load(stream)
    # ok: B506
    yaml.safe_load(stream)
    # ok: B506
    json.load(stream)
    # ok: B506
    yaml.load(stream)  # nosec
    # ok: B506
    yaml.load(stream)  # nosec B506
    # ok: B506
    yaml.load(stream)  # nosec yaml_load
    # ruleid: B506
    yaml.load(stream)  # nosec B301
