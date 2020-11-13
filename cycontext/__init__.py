from .context_component import ConTextComponent, DEFAULT_RULES_FILEPATH
from .context_item import ConTextItem
from ._version import __version__

import warnings
warnings.simplefilter('once', DeprecationWarning)
warnings.warn("cycontext is now *deprecated*. Please use medspacy.context instead: `pip install medspacy`", RuntimeWarning)

__all__ = ["ConTextComponent", "ConTextItem", "DEFAULT_RULES_FILEPATH"]
