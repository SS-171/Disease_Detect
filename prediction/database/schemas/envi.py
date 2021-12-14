def enviEntity(item) -> dict:
    return {
        "temperature": str(item["image_url"]),
        "humidity": item["status"],
        "created_at" : item["created_at"]

    }

def envisEntity(entity) -> list:
    return [enviEntity(item) for item in entity]