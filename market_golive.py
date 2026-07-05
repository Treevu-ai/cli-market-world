"""Shim — canonical implementation in cli-market-core (``market_core.market_golive``).

World keeps this top-level module for backward-compatible imports
(``from market_golive import go_live_summary``).

Note: ``go_live_summary`` (in core) internally does a bare
``from market_funnel import activation_summary, funnel_summary`` — that
import is NOT shimmed to core and resolves via sys.path to world's own
local ``market_funnel.py`` (unchanged), which keeps world's existing
noise-filtering defaults exactly as before. See ``market_funnel.py``'s
docstring for why that module isn't shimmed here.
"""

from market_core.market_golive import *  # noqa: F403,F401
