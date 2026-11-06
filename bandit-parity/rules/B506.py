import yaml
from yaml import SafeLoader, CSafeLoader
from yaml import load as parse

# ruleid: B506
yaml.load(data)
# ruleid: B506
parse(data, Loader=yaml.Loader)
# ok: B506
yaml.safe_load(data)
# ok: B506
yaml.load(data, Loader=yaml.SafeLoader)
# ok: B506
yaml.load(data, Loader=yaml.CSafeLoader)
# ok: B506
yaml.load(data, SafeLoader)
# ok: B506
yaml.load(data, CSafeLoader)
# ok: B506
yaml.load(data)  # nosec
# ok: B506
yaml.load(data)  # nosec yaml_load
# ruleid: B506
yaml.load(data)  # nosec B602
# ruleid: B506
yaml.load("#nosec")
