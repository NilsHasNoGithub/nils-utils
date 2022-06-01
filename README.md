## Experiment tools

### Example
```python
from nils_utils.experiment_tools import load_from_yaml
from dataclasses import dataclass
import io

@load_from_cfg_file(custom_parse={"param2": lambda x: 2 * x})
@dataclass  # dataclass not necessary, but adds normal dataclass functionality
class Config:
    param1: int
    param2: int
    param3: float = 2.0
    param4: str = "oi"

# Load from a yaml file which has at least all non-default parameter values as keys
yaml = """
param1: 1
param2: 2
param3: 4.5
"""
    # Same for toml
toml = """
param1 = 1
param2 = 2
param3 = 4.5
"""

cfg_yaml: Config = Config.from_yaml_file(io.BytesIO(yaml.encode("utf-8")))
cfg_toml: Config = Config.from_toml_file(io.BytesIO(toml.encode("utf-8")))
assert cfg_yaml == cfg_toml == Config(1, 4, 4.5)

# Load multiple configurations using a multi-conf format
# Multi conf is a yaml file with an entry base 'base', which is the standard configuration
# And an optional key 'deltas', a list of entries which contain differences compared to base
yaml = """
base:
    param1: 1
    param2: 2
    param3: 4.5
deltas:
    - param2: 4
      param3: 1.0
    - param1: 2
      param4: "hello world"
"""

toml = """
[base]
param1 = 1
param2 = 3
param3 = 4.5

[[deltas]]
param2 = 4
param3 = 1.0

[[deltas]]
param1 = 2
param4 = "hello world"
"""

cfgs_yaml: List[Config] = Config.from_multi_conf_yaml_file(
    io.BytesIO(yaml.encode("utf-8"))
)
cfgs_toml: List[Config] = Config.from_multi_conf_toml_file(
    io.BytesIO(toml.encode("utf-8"))
)
assert cfgs_yaml == cfgs_toml == [
    Config(1, 4, 4.5),
    Config(1, 8, 1.0),
    Config(2, 4, 4.5, "hello world"),
]

# Load configuration from a dictionary (also taking into account custom_parse)
config_dict = {
    "param1": 1,
    "param2": 2,
    "param3": 4.5,
}
cfg: Config = Config.from_dict(config_dict)
assert cfg == Config(1, 4, 4.5)
```
