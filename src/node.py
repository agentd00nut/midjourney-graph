from dataclasses import asdict, astuple, dataclass, field
from hashlib import md5
from typing import Type

from src.edge import Edge
from src.job import Job, jobFromJson
from src.mj import mj_POST

from enum import Enum


class NodeType(Enum):
    variation = "variation"
    upsample = "upsample"
    prompt = "prompt"
    reference = "reference"


@dataclass(order=True)
class Node:
    """Keeps a simplified representation of a job in midjourney to be shown."""

    id: str = field(default_factory=lambda: "")
    image: str | None = field(default_factory=lambda: "")
    reference_job_id: str | None = field(default_factory=lambda: None)
    reference_image_num: str | None = field(default_factory=lambda: None)
    prompt: str | None = field(default_factory=lambda: None)
    label: str | None = field(default_factory=lambda: None)
    full_command: str | None = field(default_factory=lambda: None)
    shape: str = "image"
    job: Job = None
    type: NodeType = field(default_factory=lambda: NodeType.variation)
    user_id: str | None = field(default_factory=lambda: None)

    def __post_init__(self):
        self.node = (
            self  # ensures we store the Node when adding to nGraph during expansion
        )

    def getTruncatedFullCommand(self):
        x = self.full_command.split(
            ">"
        )  # TODO:: this is totally going to bomb unless MJ always prepends image prompts to full command strings instead of where they show up in the prompt, a better solution would be to
        return (
            x[1][1:] if len(x) > 1 else x[0]
        )  # x[1][1:]... the [1:] removes the trailing space left after the split

    def getPromptNode(self):
        return Node(
            id=self.getTruncatedFullCommand(),
            shape="box",
            prompt=self.prompt,
            label=self.getTruncatedFullCommand(),
            full_command=self.full_command,
            job=None,
            user_id=self.user_id,  # TODO:: Ah; i should just use __getattr__ to fetch these from the job object
            type=NodeType.prompt,
        )

    def getPromptEdge(self):
        return Edge(
            id=self.prompt + "|" + self.id,
            from_=self.getTruncatedFullCommand(),
            to=self.id,
            label="",
        )

    def getReferenceNodeNoRequest(self):
        if self.reference_job_id is not None:
            return Node(
                id=self.reference_job_id,
                shape="text",
                prompt=self.prompt,
                label="temp",
                full_command=self.full_command,
                job=None,
                type=NodeType.reference,
            )
        return None

    def getReferenceEdge(self):
        if self.reference_job_id is not None:
            label = (
                str(int(self.reference_image_num) + 1)
                if self.reference_image_num is not None
                else None
            )
            return Edge(
                id=self.reference_job_id + "|" + self.id,
                from_=self.reference_job_id,
                to=self.id,
                label=label,
            )

    def getDiscordLink(self):
        if self.job is not None:
            # 662267976984297473 == guild_id
            return f"https://discord.com/channels/662267976984297473/{self.job.platform_thread_id}/{self.job.platform_message_id}"
        return None

    def __hash__(self):
        """Uses the id of the node (from midjourney) as the hash, letting us add it into nxgraphs"""
        return self.id.__hash__()

    def asvisDCCData(self):
        return {
            "id": self.id,
            "shape": self.shape,
            "image": self.image,
            "value": 1,
            # "reference_job_id": self.reference_job_id,
            # "reference_image_num": self.reference_image_num,
            "prompt": self.prompt,
            "label": self.id if self.type == NodeType.prompt else "",
            "type": str(self.type),
        }

    # def __getitem__(self,key):
    #     """Allows unpacking the Node as the attributes to a Node in a nxgraph easily!"""
    #     return self.__getattribute__(key)

    def __add__(self, other):
        """
        Allows adding two nodes together to make a new node, only if their ids are equivilent, otherwise throws an exception.

        The new node will contain a mix of data from both nodes, always prefering to take data that is not None, null, or empty.

        If an attribute is equivilent between the two Nodes then it will prefer the self attribute.
        """
        if self.id != other.id:
            raise Exception("Nodes must have the same id to be added together!")
        label = self.label if self.label is not None else other.label
        return Node(
            id=self.id,
            image=self.image or other.image,
            reference_job_id=self.reference_job_id or other.reference_job_id,
            reference_image_num=self.reference_image_num or other.reference_image_num,
            prompt=self.prompt or other.prompt,
            label=self.label if self.label != "temp" else other.label,
            full_command=self.full_command or other.full_command,
            job=self.job or other.job,
            type=self.type or other.type,
        )


def nodeFromJob(job: Job):
    """Converts a job to a node."""
    nodeType = (
        NodeType.upsample if job.jobType == "yfcc_upsample" else NodeType.variation
    )
    return Node(
        id=job.id,
        image=job.image,
        reference_job_id=job.reference_job_id,
        reference_image_num=job.reference_image_num,
        prompt=job.prompt,
        label=job.id,
        full_command=job.full_command,
        shape="image",
        job=job,
        type=nodeType,
        user_id=job.user_id,
    )
