from src.pipesay.core.pipeline import Pipeline
from src.pipesay.core.registry import register

PROCESSER_REGISTRY: dict = {}


def processer(name: str | None = None):
    return register(PROCESSER_REGISTRY, name)


class Processer(Pipeline):
    registry = PROCESSER_REGISTRY
    section = 'pipeline'
    label = 'Processer'

    def process(self, sentences: list) -> list:
        return self.run(sentences)

    @staticmethod
    def list_processers():
        Processer.list_all()