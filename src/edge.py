from dataclasses import asdict, dataclass, field

##
@dataclass
class Edge:
    id: str
    from_: str
    to: str
    label: str = field(default="")

    def asGraphEdge(self):
        return {"id": self.id, "from": self.from_, "to": self.to, "label": self.label}
