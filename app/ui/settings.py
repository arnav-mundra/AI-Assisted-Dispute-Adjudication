"""Run settings chosen in the sidebar and shared by every page."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    engine: str          # auto | llm | rules
    model: str
    prompt_style: str    # zero_shot | facts | cot
    retrieval: str       # lexical | bm25 | dense | hybrid
    top_k: int
    llm_ready: bool
    guard: bool = False          # escalate when the rules engine disagrees with the LLM
    min_confidence: float = 0.0  # escalate LLM rulings below this confidence

    @property
    def effective_engine(self) -> str:
        if self.engine == "auto":
            return "llm" if self.llm_ready else "rules"
        return self.engine

    @property
    def key(self) -> str:
        return (f"{self.effective_engine}|{self.model}|{self.prompt_style}|{self.retrieval}|{self.top_k}"
                f"|{self.guard}|{self.min_confidence}")

    def describe(self) -> str:
        if self.effective_engine == "rules":
            return "Rules engine (offline)"
        return f"{self.model}, {self.prompt_style.replace('_', '-')} prompt"
