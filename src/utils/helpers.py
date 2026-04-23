from __future__ import annotations

from math import erf, exp, log, pi, sqrt
from typing import Iterable

import numpy as np
import pandas as pd


def ensure_parent(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
