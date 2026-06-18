from collections.abc import AsyncIterator

from pipecat.utils.text.base_text_aggregator import Aggregation, AggregationType
from pipecat.utils.text.simple_text_aggregator import SimpleTextAggregator


class BufferedSentenceAggregator(SimpleTextAggregator):
    def __init__(self, min_chars: int = 200, **kwargs):
        super().__init__(**kwargs)
        self._min_chars = min_chars
        self._pending = ""

    async def aggregate(self, text: str) -> AsyncIterator[Aggregation]:
        if self._aggregation_type == AggregationType.TOKEN:
            if text:
                yield Aggregation(text=text, type=AggregationType.TOKEN)
            return

        for char in text:
            self._text += char

            result = await self._check_sentence_with_lookahead(char)
            if result:
                self._pending += result.text + " "
                if len(self._pending) >= self._min_chars:
                    yield Aggregation(
                        text=self._pending.strip(),
                        type=AggregationType.SENTENCE,
                    )
                    self._pending = ""

    async def flush(self) -> Aggregation | None:
        # Save pending before super().flush() because it calls self.reset()
        # which clears _pending
        saved_pending = self._pending
        self._pending = ""
        remaining = await super().flush()
        if remaining:
            saved_pending += remaining.text + " "
        if saved_pending:
            return Aggregation(text=saved_pending.strip(), type=AggregationType.SENTENCE)
        return None

    async def handle_interruption(self):
        await super().handle_interruption()
        self._pending = ""

    async def reset(self):
        await super().reset()
        self._pending = ""

    @property
    def text(self) -> Aggregation:
        full = (self._pending + self._text).strip()
        if full:
            return Aggregation(text=full, type=AggregationType.SENTENCE)
        return Aggregation(text="", type=AggregationType.SENTENCE)
