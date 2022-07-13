from dataclasses import asdict, dataclass, field
from hashlib import md5

from src.edge import Edge
from src.job import Job, jobFromJson
from src.mj import makeMidJourneyRequest


@dataclass
class Node:
    """Keeps a simplified representation of a job in midjourney to be shown."""
    id: str
    image: str | None
    reference_job_id: str | None
    reference_image_num: str | None
    prompt: str
    label: str
    full_command: str
    shape: str = "image"
    isPromptNode: bool = False
    isReferenceNode: bool = False
    job: Job = None

    def __post_init__(self):
        if self.isPromptNode:
            self.label = self.full_command

    def setJob(self, j):
        self.job = j

    def promptNode(self):
        return Node(id=self.prompt, image=None, reference_job_id=None, reference_image_num=None, shape="text", prompt=self.prompt, label=self.prompt, full_command=self.full_command, isPromptNode=True, job=self.job)

    def promptEdge(self):
        return Edge(id=self.prompt+"|"+self.id, from_=self.prompt, to=self.id)

    def getReferenceNodeNoRequest(self):
        if self.reference_job_id is not None:
            return Node(id=self.reference_job_id, image=None, reference_job_id=None, reference_image_num=None, shape="text", prompt=self.prompt, label=self.prompt, full_command=self.full_command, isReferenceNode=True, job=self.job)
        return None

    def getReferenceNode(self):
        if self.reference_job_id is not None:
            r = makeMidJourneyRequest(
                "https://www.midjourney.com/api/app/job-status/", "{\"jobIds\":[\""+self.reference_job_id+"\"]}")
            job = jobFromJson(r.json()[0])
            return nodeFromJob(job)

    def referenceEdge(self):
        if self.reference_job_id is not None:
            label = str(int(self.reference_image_num) +
                        1) if self.reference_image_num is not None else None
            return Edge(id=self.id[0:4]+"|"+self.reference_job_id[0:4], from_=self.reference_job_id, to=self.id, label=label)

    def gotoDiscord(self):
        if self.job is not None:
            # 662267976984297473 == guild_id
            return f"https://discord.com/channels/662267976984297473/{self.job.platform_thread_id}/{self.job.platform_message_id}"
        return None


def nodeFromJob(job: Job):
    return Node(id=job.id, image=job.image, reference_job_id=job.reference_job_id, reference_image_num=job.reference_image_num, prompt=job.prompt, label=job.id, full_command=job.full_command, shape="image", job=job)
