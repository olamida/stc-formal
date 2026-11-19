"""stc-formal: runtime monitoring, loss bound and counterexample search for stc-corridors."""
import os
import sys

# Use an installed `stc` package if present; otherwise fall back to the sibling checkout.
try:
    import stc  # noqa: F401
except ImportError:                                           # pragma: no cover
    _sib = os.path.join(os.path.dirname(__file__), "..", "..", "..", "stc-corridors", "src")
    sys.path.insert(0, os.path.abspath(_sib))
    import stc  # noqa: F401

from .monitor import (Always, Eventually, Pred, collisions_from_trace, robustness,  # noqa: E402
                      separation_pred, goal_pred)

__all__ = ["Always", "Eventually", "Pred", "collisions_from_trace", "robustness",
           "separation_pred", "goal_pred"]
