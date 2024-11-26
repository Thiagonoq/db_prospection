from src.database import mongo
from src.helpers.nlp import process_text


async def get_product_data(
    database: str, product: str, include: str = None, limit: int = 0
):
    include_keys = {}

    if include:
        for key in include.split(","):
            include_keys[key] = 1

    db = mongo.products(database)

    pipeline = [
        {"$match": {"$text": {"$search": process_text(product)}}},
        {
            "$project": {
                "_id": 0,
                **include_keys,
                "score": {"$meta": "textScore"},
            }
        },
        {"$sort": {"score": {"$meta": "textScore"}}},
        {"$match": {"score": {"$gte": 120}}},
    ]

    if limit:
        pipeline.append({"$limit": limit})

    search = await db.aggregate(pipeline).to_list(None)

    if len(search) == 1 and limit == 1:
        return search[0]

    return search
