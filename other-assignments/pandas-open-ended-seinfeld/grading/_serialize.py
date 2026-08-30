"""Turn pandas answers into plain JSON-able structures for snapshotting."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _scalar(value):
    if value is None:
        return None
    if isinstance(value, (np.generic,)):
        value = value.item()
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return round(value, 6)
    return str(value)


def _labels(index: pd.Index):
    if isinstance(index, pd.MultiIndex):
        return [[_scalar(v) for v in key] for key in index]
    return [_scalar(v) for v in index]


def _index_names(index: pd.Index):
    if isinstance(index, pd.MultiIndex):
        return list(index.names)
    return index.name


def to_jsonable(obj):
    """Canonical, diff-friendly representation of a graded answer."""
    if isinstance(obj, pd.DataFrame):
        return {
            "kind": "DataFrame",
            "index_name": _index_names(obj.index),
            "index": _labels(obj.index),
            "columns": [str(c) for c in obj.columns],
            "data": [[_scalar(v) for v in row] for row in obj.to_numpy().tolist()],
        }
    if isinstance(obj, pd.Series):
        return {
            "kind": "Series",
            "name": obj.name,
            "index_name": _index_names(obj.index),
            "index": _labels(obj.index),
            "values": [_scalar(v) for v in obj.tolist()],
        }
    if isinstance(obj, tuple):
        return {"kind": "tuple", "values": [_scalar(v) for v in obj]}
    return {"kind": "scalar", "value": _scalar(obj)}
