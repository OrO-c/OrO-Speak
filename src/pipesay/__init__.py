# src/pipesay/__init__.py
from pipesay.core.pipeline import Pipeline
from pipesay.core.registry import register
from pipesay.fetcher.fetcher import Fetcher
from pipesay.outputers.base import Outputer
from pipesay.processor.base import Processor

__version__ = "0.0.1"
__all__ = ["Fetcher", "Outputer", "Pipeline", "Processor", "register"]