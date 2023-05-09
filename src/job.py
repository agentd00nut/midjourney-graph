from dataclasses import dataclass
import json


@dataclass
class Job:
    id: str
    image_paths: list[str]
    image: str
    status: str
    ## duration: str
    enqueue_time: str
    reference_job_id: str
    reference_image_num: int
    reference_image_path: str
    prompt: str
    full_command: str
    platform: str
    platform_channel: str
    platform_channel_id: str
    platform_message_id: str
    platform_thread_id: str
    guild_id: str
    jobType: str
    user_id: str


def jobFromJson(j):
    print("jobFromJson: ", j)

    if "id" not in j:
        j = json.loads(j)
        if "id" not in j:
            print("jobFromJson: no id, j is: ", j)
            return None
    
    job_image_root = (
        "https://cdn.midjourney.com/" + j["id"] + "/"
    )

    paths=[]
    img=""
    if "image_paths" in j:
        paths = j["image_paths"]
        img=paths[0]
    if len(paths) == 1:
        img=job_image_root + "grid_0.webp"
    return Job(
        id=j["id"],
        image_paths=paths,
        image=img,
        status=j["current_status"],
        enqueue_time=j["enqueue_time"],
        reference_job_id=j["reference_job_id"],
        reference_image_num=j["reference_image_num"],
        reference_image_path="https://cdn.midjourney.com/"
        + j["reference_job_id"]
        + "/grid_0"
        # + j["reference_image_num"]
        # + ".png"
        if j["reference_job_id"] is not None else None,
        prompt=j["prompt"],
        full_command=j["full_command"],
        platform=j["platform"],
        guild_id=j["guild_id"],
        platform_channel=j["platform_channel"],
        platform_channel_id=j["platform_channel_id"],
        platform_message_id=j["platform_message_id"],
        platform_thread_id=j["platform_thread_id"],
        jobType=j["type"],
        user_id=j["user_id"],
    )
