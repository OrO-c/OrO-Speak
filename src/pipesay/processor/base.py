from src.pipesay.core.pipeline import Pipeline
from src.pipesay.core.registry import register

PROCESSOR_REGISTRY: dict = {}


def processor(name: str | None = None):
    return register(PROCESSOR_REGISTRY, name)


class Processor(Pipeline):
    registry = PROCESSOR_REGISTRY
    section = 'pipeline'
    label = 'Processor'

    def process(self, sentences: list) -> list:
        return self.run(sentences)

    @staticmethod
    def list_processers():
        Processor.list_all()