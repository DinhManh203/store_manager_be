from bson import ObjectId

def convert_objectid_to_str(item: dict) -> dict:
    if "_id" in item:
        item["id"] = str(item["_id"])
        del item["_id"]
    return item

def is_valid_objectid(id_str: str) -> bool:
    return ObjectId.is_valid(id_str)
