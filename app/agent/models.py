from dataclasses import dataclass



@dataclass
class AgentState:

    question:str


    context:list[str]


    steps:list[str]


    answer:str | None = None