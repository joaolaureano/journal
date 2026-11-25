import importlib

import pytest


@pytest.mark.parametrize("layer", ["domain", "ports", "adapters", "app"])
def test_layer_is_importable(layer):
    importlib.import_module(f"journal.{layer}")
