from dataclasses import dataclass


@dataclass
class Job:
    id: str
    image_paths: list[str]
    image: str
    status: str
    # duration: str
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
    platform_channel: str
    platform_channel_id: str
    platform_message_id: str
    platform_thread_id: str
    jobType: str


def jobFromJson(j):

    job_image_root = (
        "https://storage.googleapis.com/dream-machines-output/" + j["id"] + "/"
    )

    return Job(
        id=j["id"],
        image_paths=j["image_paths"],
        image=job_image_root + "grid_0.webp"
        if len(j["image_paths"]) == 4
        else j["image_paths"][0],
        status=j["current_status"],
        enqueue_time=j["enqueue_time"],
        reference_job_id=j["reference_job_id"],
        reference_image_num=j["reference_image_num"],
        reference_image_path="https://storage.googleapis.com/dream-machines-output/"
        + j["reference_job_id"]
        + "/0_"
        + j["reference_image_num"]
        + ".png"
        if j["reference_job_id"] is not None
        else None,
        prompt=j["prompt"],
        full_command=j["full_command"],
        platform=j["platform"],
        guild_id=j["guild_id"],
        platform_channel=j["platform_channel"],
        platform_channel_id=j["platform_channel_id"],
        platform_message_id=j["platform_message_id"],
        platform_thread_id=j["platform_thread_id"],
        jobType=j["type"],
    )
