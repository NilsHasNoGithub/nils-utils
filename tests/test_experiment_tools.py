from dataclasses import dataclass
import pytest
from src import experiment_tools
from src.experiment_tools.config_gen import load_from_yaml
import io

def test_decorator():

    yaml = \
        "param1: 5\n" + \
        "param2: 1\n" + \
        "param3: 5.5\n"

    @load_from_yaml(custom_parse={"param2": lambda x: 2 * x})
    @dataclass
    class Config:
        param1: int
        param2: int
        param3: float = 2.0
        param4: str = "oi"

    # cfg = Config(1, 2.0, "oi")
    # cfg = Config()
    cfg = Config.from_yaml_file(io.BytesIO(yaml.encode("utf-8")))
    print(cfg)

    assert cfg.param1 == 5
    assert cfg.param2 == 2
    assert cfg.param3 == 5.5
    assert cfg.param4 == "oi"

    ...