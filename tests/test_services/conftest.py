"""
The goal of this testing module is simple: just test the
services in isolation, and do not interact at all with the
web endpoints.
"""

import io

import pytest_asyncio
import requests
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from soposerve.database import BEANIE_MODELS

### -- Dependency Injection Fixtures -- ###

@pytest_asyncio.fixture(scope="session", autouse=True)
async def database(database_container):
    db = AsyncIOMotorClient(database_container["url"])
    await init_beanie(
        database=db.db_name,
        document_models=BEANIE_MODELS,
    )

    yield db

### -- Data Service Fixtures -- ###

@pytest_asyncio.fixture(scope="session")
async def created_user(database):
    from soposerve.service import users

    user = await users.create(
        name="test_user",
        privileges=[users.Privilege.LIST]
    )

    yield user

    await users.delete(user.name)

@pytest_asyncio.fixture(scope="session")
async def created_full_product(database, storage, created_user):
    from soposerve.service import product

    PRODUCT_NAME = "My Favourite Product"
    PRODUCT_DESCRIPTION = "The best product ever."
    FILE_CONTENTS = b"0x0" * 1024
    SOURCES = [
        product.PreUploadFile(
            name=f"test_{x}.txt",
            size=1024,
            checksum="eh_whatever"
        ) for x in range(4)
    ]

    data, file_puts = await product.create(
        name=PRODUCT_NAME,
        description=PRODUCT_DESCRIPTION,
        metadata=None,
        sources=SOURCES,
        user=created_user,
        storage=storage
    )

    assert not await product.confirm(PRODUCT_NAME, storage)

    with io.BytesIO(FILE_CONTENTS) as f:
        for put in file_puts.values():
            # Must go back to the start or we write 0 bytes!
            f.seek(0)
            requests.put(put, f)

    assert await product.confirm(PRODUCT_NAME, storage)

    yield data

    await product.delete(
        name=data.name,
        storage=storage,
        data=True
    )

@pytest_asyncio.fixture(scope="session")
async def created_collection(database):
    from soposerve.service import collection

    COLLECTION_NAME = "My Favourite Collection"
    COLLECTION_DESCRIPTION = "The best collection ever."

    data = await collection.create(
        name=COLLECTION_NAME,
        description=COLLECTION_DESCRIPTION,
    )

    yield data

    await collection.delete(
        name=data.name,
    )