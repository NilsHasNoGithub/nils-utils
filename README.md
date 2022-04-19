## Experiment tools

### Example
```python
@load_from_yaml(custom_parse={"param2": lambda x: 2 * x})
@dataclass
class Config:
    param1: int
    param2: int
    param3: float = 2.0
    param4: str = "oi"

Config.from_yaml_file(...)
Config.from_multi_conf_yaml_file(...)
Config.from_dict(...)
```