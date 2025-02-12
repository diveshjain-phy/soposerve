"""
Web frontend for hippo. This consumes the service layer.

NOTE: Code coverage is an explicit NON-goal for the web
      frontend, and as such it is excluded from our
      coverage metrics.
"""

import asyncio

from beanie import PydanticObjectId
from fastapi import Request

from hipposerve.service import collection, product

from .auth import PotentialLoggedInUser
from .auth import router as auth_router
from .router import static_files as static_files
from .router import templates, web_router
from .search import router as search_router

web_router.include_router(search_router)
web_router.include_router(auth_router)


@web_router.get("/")
async def index(request: Request, user: PotentialLoggedInUser):
    products = await product.read_most_recent(fetch_links=True, maximum=16, user=user)
    collections = await collection.read_most_recent(
        fetch_links=True, maximum=16, user=user
    )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "products": products,
            "collections": collections,
            "user": user,
        },
    )


@web_router.get("/products/{id}")
async def product_view(request: Request, id: str, user: PotentialLoggedInUser):
    product_instance = await product.read_by_id(id, user)
    sources = await product.read_files(product_instance, storage=request.app.storage)
    # Grab the history!
    latest_version = await product.walk_to_current(product_instance, user)
    version_history = await product.walk_history(latest_version)

    return templates.TemplateResponse(
        "product.html",
        {
            "request": request,
            "product": product_instance,
            "sources": sources,
            "versions": version_history,
            "user": user,
        },
    )


@web_router.get("/collections/{id}")
async def collection_view(
    request: Request, id: PydanticObjectId, user: PotentialLoggedInUser
):
    collection_instance = await collection.read(id)
    visibility_checks = await asyncio.gather(
        *(
            product.check_visibility_access(product_item, user)
            for product_item in collection_instance.products
        )
    )
    collection_instance.products = [
        product_item
        for product_item, visibility in zip(
            collection_instance.products, visibility_checks
        )
        if visibility
    ]
    return templates.TemplateResponse(
        "collection.html",
        {"request": request, "collection": collection_instance, "user": user},
    )
