"""
The database access layer for hippo. Uses MongoDB and Beanie.
"""

from datetime import datetime
from enum import Enum

import pymongo
from beanie import BackLink, Document, Indexed, Link, PydanticObjectId
from pydantic import BaseModel, Field

from hippometa import ALL_METADATA_TYPE


class CollectionPolicy(Enum):
    # What to do when versions are revved of products.
    # Keep track of all versions of the product in the collection.
    ALL = "all"
    # Keep track of all new versions of the product in the collection.
    # E.g. if v2 is added to a collection, v1 is _not_ but all future
    # versions will be tracked as part of that collection.
    NEW = "new"
    # Keep track of only the 'current' version of the product.
    CURRENT = "current"
    # Keep track of only a 'fixed' version of the product. So if v2 is
    # added to the collection, and v3 is created, only v2 is tracked in
    # the collection.
    FIXED = "fixed"


class User(Document):
    name: Indexed(str, unique=True)
    email: str | None
    last_access_time: datetime | None


class FileMetadata(BaseModel):
    """
    Object containing the metadata from a single file.
    """

    id: PydanticObjectId
    name: str
    description: str | None = None
    uploader: str
    uuid: str
    bucket: str
    size: int
    checksum: str
    available: bool = True


class File(Document, FileMetadata):
    # Information for multi-part uploads (private)
    multipart: bool = False
    number_of_parts: int = 1
    upload_id: str | None = None
    multipart_batch_size: int | None = None
    multipart_closed: bool = False

    def to_metadata(self) -> FileMetadata:
        return FileMetadata(
            id=self.id,
            name=self.name,
            description=self.description,
            uploader=self.uploader,
            uuid=self.uuid,
            bucket=self.bucket,
            size=self.size,
            checksum=self.checksum,
            available=self.available,
        )


class ProductMetadata(BaseModel):
    """
    Object containing the metadata from a single version of a product.
    """

    id: PydanticObjectId

    name: str
    description: str
    metadata: ALL_METADATA_TYPE

    uploaded: datetime
    updated: datetime

    current: bool
    version: str

    sources: list[FileMetadata]
    owner: str

    replaces: str | None

    child_of: list[PydanticObjectId]
    parent_of: list[PydanticObjectId]

    collections: list[PydanticObjectId]


class ProtectedDocument(Document):
    readers: list[str] = Field(default_factory=list)
    writers: list[str] = Field(default_factory=lambda: ["admin"])
    owner: str


class Product(ProtectedDocument, ProductMetadata):
    name: Indexed(str, pymongo.TEXT)

    sources: list[File]

    replaces: Link["Product"] | None = None

    child_of: list[Link["Product"]] = []
    parent_of: list[BackLink["Product"]] = Field(
        json_schema_extra={"original_field": "child_of"}, default=[]
    )

    collections: list[Link["Collection"]] = []
    collection_policies: list[CollectionPolicy] = []

    def to_metadata(self) -> ProductMetadata:
        return ProductMetadata(
            id=self.id,
            name=self.name,
            description=self.description,
            metadata=self.metadata,
            uploaded=self.uploaded,
            updated=self.updated,
            current=self.current,
            version=self.version,
            sources=[x.to_metadata() for x in self.sources],
            owner=self.owner,
            replaces=self.replaces.version if self.replaces is not None else None,
            child_of=[x.id for x in self.child_of],
            parent_of=[x.id for x in self.parent_of],
            collections=[x.id for x in self.collections],
        )


class CollectionMetadata(BaseModel):
    """
    Base model for a collection.
    """

    id: PydanticObjectId

    name: str
    description: str

    products: list[ProductMetadata]
    child_collections: list[PydanticObjectId]
    parent_collections: list[PydanticObjectId]


class Collection(ProtectedDocument, CollectionMetadata):
    # TODO: Implement updated time for collections.

    name: Indexed(str, pymongo.TEXT)
    products: list[BackLink[Product]] = Field(
        json_schema_extra={"original_field": "collections"}
    )
    child_collections: list[Link["Collection"]] = []
    parent_collections: list[BackLink["Collection"]] = Field(
        json_schema_extra={"original_field": "child_collections"}
    )


BEANIE_MODELS = [User, File, Product, Collection]
