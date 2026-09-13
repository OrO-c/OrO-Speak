from core.pipeline import Pipeline
from core.registry import register

SPEAKER_REGISTRY: dict = {}


def speaker(name: str | None = None):
    return register(SPEAKER_REGISTRY, name)


class Speaker(Pipeline):
    registry = SPEAKER_REGISTRY
    section = 'pipeline'
    label = 'Speaker'

    def process(self, sentences: list) -> list:
        return self.run(sentences)

    @staticmethod
    def list_speakers():
        Speaker.list_all()