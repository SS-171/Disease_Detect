import io
from PIL import Image
def plantEntity(item) -> dict:
    return {
        "id" : str(item["_id"]),
        "image_url": str(item["image_url"]),
        "status": item["status"],
        "created_at" : item["created_at"]

    }

def plantsEntity(entity) -> list:
    return [plantEntity(item) for item in entity]