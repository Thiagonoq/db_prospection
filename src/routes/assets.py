import json
import logging
import mimetypes
import uuid
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from bson import ObjectId
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from firebase_admin import storage
from pydantic import BaseModel, Field

from config import FIREBASE_STORAGE_BUCKET, TMP_PATH
from src.auth.login import get_current_user
from src.database import mongo
from src.helpers import date
from src.helpers.download import download_file
from src.helpers.is_ import Is
from src.helpers.string import slugify
from src.models.client import ClientModel
from src.routes.client import parse_form

router = APIRouter(prefix="/assets", tags=["GPT"])


class AssetType(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"
    model = "model"
    document = "document"


class AssetSubtype(str, Enum):
    vector = "vector"


class AssetOrigin(str, Enum):
    firebase = "firebase"
    external = "external"


class File(BaseModel):
    size: int
    filename: str
    mimetype: str


class Framing(BaseModel):
    x: Union[int, float]
    y: Union[int, float]
    width: Union[int, float]
    height: Union[int, float]


class AssetOptions(BaseModel):
    face_detection: Optional[bool] = None
    framing: Optional[dict[str, Framing]] = None


class Asset(BaseModel):
    _id: str
    name: str
    niche: str
    type: AssetType
    origin: AssetOrigin
    categories: list[str] = []

    owner: Optional[str] = None
    is_public: Optional[bool] = False

    subtype: Optional[AssetSubtype] = None

    url: Optional[str] = None
    bucket: Optional[str] = None
    file: Optional[File] = None

    options: Optional[AssetOptions] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Find(BaseModel):
    _id: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    niche: Optional[str] = None
    bucket: Optional[str] = None
    type: Optional[AssetType] = None
    origin: Optional[AssetOrigin] = None
    subtype: Optional[AssetSubtype] = None
    categories: Optional[list[str]] = None


class Projection(BaseModel):
    name: Optional[int] = 1
    type: Optional[int] = 1
    subtype: Optional[int] = 1
    origin: Optional[int] = 1
    url: Optional[int] = 1
    bucket: Optional[int] = 1
    file: Optional[int] = 1
    options: Optional[int] = 1
    created_at: Optional[int] = 1
    updated_at: Optional[int] = 1
    categories: Optional[int] = 1
    niche: Optional[int] = 1
    owner: Optional[int] = 1
    is_public: Optional[int] = 1


class GetAssets(BaseModel):
    find: Find
    skip: Optional[int] = 0
    limit: Optional[int] = 10
    projection: Optional[Projection] = None
    my_content: Optional[bool] = Field(False, alias="myContent")
    exclude_categories: Optional[list[str]] = None


@router.post("/list")
async def get_assets(data: GetAssets, client: ClientModel = Depends(get_current_user)):
    find = {
        k: v
        for k, v in data.find.model_dump(exclude_none=True, exclude_unset=True).items()
        if v
    }

    if data.find.name:
        find["name"] = {"$regex": find["name"], "$options": "i"}

    if data.find.categories:
        parsed_categories = [ObjectId(category) for category in data.find.categories]

        find["categories"] = {"$in": parsed_categories}

    if data.exclude_categories:
        parsed_categories = [ObjectId(category) for category in data.exclude_categories]

        find["categories"] = {"$nin": parsed_categories}

    default_projection = Projection(
        _id=1, name=1, type=1, subtype=1, categories=1, url=1
    )
    projection = data.projection or default_projection

    response_data = []

    if not client.is_dev:
        projection = default_projection

    if not client.is_dev or data.my_content:
        find.update(
            {
                "$or": [{"is_public": True}, {"owner": ObjectId(client.id)}],
                "niche": client.niche,
            }
        )

    projection = projection.model_dump(
        exclude_none=True, exclude_unset=True, include={"_id": 1}
    )

    extra_collections = []

    if client.is_dev:
        for collection in await mongo.database.list_collection_names():
            if collection.startswith("assets_"):
                extra_collections.append(
                    {
                        "$unionWith": {
                            "coll": collection,
                            "pipeline": [{"$match": find}],
                        }
                    }
                )
    else:
        client_available_collections = [client.niche, "logos"]

        for collection in client_available_collections:
            extra_collections.append(
                {
                    "$unionWith": {
                        "coll": f"assets_{collection}",
                        "pipeline": [{"$match": find}],
                    }
                }
            )

    pipeline = [
        {"$match": find},
        *extra_collections,
        {"$skip": data.skip},
        {"$limit": data.limit},
    ]

    if projection:
        pipeline.append({"$project": projection})

    pipeline.append(
        {
            "$lookup": {
                "from": "categories",
                "localField": "categories",
                "foreignField": "_id",
                "as": "categories",
            }
        }
    )

    print(pipeline)

    cursor = mongo.database.assets.aggregate(pipeline)

    response_data = []

    async for asset in cursor:
        asset["id"] = str(asset.pop("_id"))

        url = asset["url"]

        split_url = url.split("/")
        split_url.insert(-1, "thumbs")
        split_url[-1] = f"{split_url[-1].split('.')[0]}_300x300.webp"

        asset["thumb"] = "/".join(split_url)

        asset["categories"] = [
            {
                "id": str(category["_id"]),
                "name": category["name"],
                "slug": category["slug"],
            }
            for category in asset["categories"]
        ]

        asset["owner"] = [str(owner) for owner in asset["owner"]]

        response_data.append(asset)

    count_assets = await mongo.database.assets.count_documents(find)
    count_hortifruti = await mongo.database.assets_hortifruti.count_documents(find)
    total_count = count_assets + count_hortifruti

    return {
        "count": total_count,
        "results": response_data,
    }


@router.get("/{asset_id}")
async def get_asset(asset_id: str, client: ClientModel = Depends(get_current_user)):
    query = {"_id": ObjectId(asset_id)}

    if not client.is_dev:
        query.update({"owner": client.client, "is_public": True, "niche": client.niche})

    asset = await mongo.database.assets.find_one()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset["id"] = str(asset.pop("_id"))

    return asset


class CreateAsset(BaseModel):
    name: str
    categories: list[str] = Field(default=[], title="Categories")
    niche: Optional[str] = None
    location: Optional[str] = None
    is_public: Optional[bool] = False
    file: Union[str, UploadFile] = Field(..., title="URL or File")

    bucket: Optional[str] = None
    options: Optional[AssetOptions] = None


def get_type_from_mimetype(mimetype: str):
    if mimetype.startswith("image"):
        return AssetType.image

    if mimetype.startswith("video"):
        return AssetType.video

    if mimetype.startswith("audio"):
        return AssetType.audio

    if mimetype.startswith("application/json"):
        return AssetType.model

    if mimetype.startswith("application/pdf"):
        return AssetType.document

    return AssetType.image


@router.post("/")
async def create_asset(
    request: Request,
    client: ClientModel = Depends(get_current_user),
):
    asset = CreateAsset(**parse_form(await request.form()))

    if not client.is_dev:
        if client.niche != asset.niche:
            asset.niche = client.niche

        asset.bucket = FIREBASE_STORAGE_BUCKET
        asset.location = f"/personal/{client.id}"

    if client.is_dev:
        if not asset.bucket:
            asset.bucket = FIREBASE_STORAGE_BUCKET

        if not asset.location:
            asset.location = f"/personal/{client.id}"

    asset_data = asset.model_dump()

    session_path = TMP_PATH / uuid.uuid4().hex
    session_path.mkdir(parents=True, exist_ok=True)

    file_data = {}

    try:
        if isinstance(asset_data["file"], str):
            if not Is.url(asset_data["file"]):
                raise HTTPException(status_code=400, detail="Invalid URL")

            if not client.is_dev:
                raise HTTPException(status_code=403, detail="Forbidden")

            file = await download_file(asset_data["file"], session_path)

            if not isinstance(file, Path):
                raise HTTPException(status_code=400, detail="Invalid file")

            size = file.stat().st_size
            filename = file.name
            mimetype = mimetypes.guess_type(filename, strict=False)[0]

            subtype = None

            if mimetype == "image/svg+xml":
                subtype = AssetSubtype.vector

            file_data.update(
                {
                    "file": {
                        "size": size,
                        "filename": filename,
                        "mimetype": mimetype,
                    },
                    "subtype": subtype,
                    "type": get_type_from_mimetype(mimetype),
                    "url": asset_data["file"],
                    "origin": AssetOrigin.external,
                }
            )
        else:
            bucket_name = (
                asset_data.get("bucket", FIREBASE_STORAGE_BUCKET)
                or FIREBASE_STORAGE_BUCKET
            )

            if not bucket_name:
                raise HTTPException(status_code=400, detail="Bucket name is required")

            bucket = storage.bucket(bucket_name)

            if not bucket.exists():
                raise HTTPException(status_code=400, detail="Bucket not found")

            file: UploadFile = asset_data["file"]

            if not file:
                raise HTTPException(status_code=400, detail="Invalid file")

            location = asset_data.get("location") or ""

            subtype = None

            if file.content_type == "image/svg+xml":
                subtype = AssetSubtype.vector

            size = len(await file.read())

            await file.seek(0)

            filename = file.filename
            mimetype = (
                file.content_type or mimetypes.guess_type(filename, strict=False)[0]
            )

            extension = Path(filename).suffix

            slugified_name = slugify(asset_data["name"])

            full_location = f"assets{location}/{slugified_name}{extension}"

            blob = bucket.blob(full_location)

            blob.upload_from_file(file.file)

            blob.make_public()

            url = blob.public_url

            file_data.update(
                {
                    "file": {
                        "size": size,
                        "filename": filename,
                        "mimetype": mimetype,
                    },
                    "subtype": subtype,
                    "bucket": bucket_name,
                    "url": url,
                    "location": full_location,
                    "type": get_type_from_mimetype(mimetype),
                    "origin": AssetOrigin.firebase,
                }
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        logging.exception(e)

        raise HTTPException(status_code=400, detail="Failed to create asset")

    if client.is_dev:
        file_data.update(
            {
                "is_public": asset_data.get("is_public", False),
                "niche": asset_data.get("niche", client.niche),
            }
        )
    else:
        file_data.update(
            {"owner": client.client, "is_public": False, "niche": client.niche}
        )

    file_data.update(
        {
            "name": asset_data["name"],
            "created_at": date.now(),
            "updated_at": date.now(),
            "options": asset_data.get("options"),
            "categories": [
                ObjectId(category) for category in asset_data.get("categories", [])
            ],
        }
    )

    result = await mongo.database.assets.insert_one(file_data)

    return {
        "message": "Asset created successfully",
        "asset": {
            "id": str(result.inserted_id),
            "name": asset_data["name"],
            "url": file_data["url"],
            "type": file_data["type"],
            "categories": [
                {
                    "id": str(category["_id"]),
                    "name": category["name"],
                    "slug": category["slug"],
                }
                for category in await mongo.database.categories.find(
                    {"_id": {"$in": file_data["categories"]}}
                ).to_list(None)
            ],
        },
    }


@router.delete("/{asset_id}")
async def delete_asset(asset_id: str, client: ClientModel = Depends(get_current_user)):
    query = {"_id": ObjectId(asset_id)}

    if not client.is_dev:
        query.update({"owner": client.client, "niche": client.niche})

    deleted = await mongo.database.assets.find_one_and_delete(query)

    if not deleted:
        raise HTTPException(status_code=404, detail="Asset not found")

    if not client.is_dev and deleted.get("is_public"):
        raise HTTPException(status_code=403, detail="Forbidden to delete public asset")

    if deleted["origin"] == AssetOrigin.firebase:
        try:
            bucket = storage.bucket(deleted["bucket"])
            blob = bucket.blob(deleted["location"])
            blob.delete()
        except Exception as e:
            logging.exception(e)

    return {"message": "Asset deleted successfully"}


class UpdateAsset(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    options: Optional[AssetOptions] = None
    categories: Optional[list[str]] = None


@router.put("/{asset_id}")
async def update_asset(
    asset_id: str, data: UpdateAsset, client: ClientModel = Depends(get_current_user)
):
    query = {"_id": ObjectId(asset_id)}

    if not client.is_dev:
        query.update({"owner": client.client, "niche": client.niche})

        if data.niche and data.niche != client.niche:
            raise HTTPException(status_code=403, detail="Forbidden to update niche")

        if data.options:
            raise HTTPException(status_code=403, detail="Forbidden to update options")

    new_data = data.model_dump(exclude_none=True, exclude_unset=True)

    if new_data.get("categories"):
        new_data["categories"] = [
            ObjectId(category) for category in new_data["categories"]
        ]

    file = await mongo.database.assets.find_one(query)

    if not file:
        raise HTTPException(status_code=404, detail="Asset not found")

    if not client.is_dev and file.get("is_public"):
        raise HTTPException(status_code=403, detail="Forbidden to update public asset")

    updated = await mongo.database.assets.find_one_and_update(query, {"$set": new_data})

    if not updated:
        raise HTTPException(status_code=404, detail="Asset not found")

    return {"message": "Asset updated successfully"}
