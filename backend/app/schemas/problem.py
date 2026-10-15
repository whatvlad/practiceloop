from pydantic import BaseModel, ConfigDict


class PublicProblem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    topic: str
    problem_latex: str
