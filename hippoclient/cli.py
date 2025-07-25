"""
A CLI interface to the hippo client.
"""

from typing import Annotated

import rich
import typer

import hippoclient as sc

from . import helper
from .core import ClientSettings, MultiCache
from .textedit import edit_product

CLIENT: sc.Client
CACHE: MultiCache
CONSOLE: rich.console.Console

# Meta-setup
APP = typer.Typer()
product_app = typer.Typer(help="Commands for dealing directly with products")
APP.add_typer(product_app, name="product")
collection_app = typer.Typer(help="Commands for dealing with collections")
APP.add_typer(collection_app, name="collection")
cache_app = typer.Typer(
    help="Maintenance commands for the cache. There are also tools for cache management in the product and collection commands."
)
APP.add_typer(cache_app, name="cache")
dev_app = typer.Typer(
    help="Developer commands, mainly used for running and testing servers during hippo development. For regular use, you can ignore these."
)
APP.add_typer(dev_app, name="dev")


@product_app.command("read")
def product_read(id: str):
    """
    Read the information of a product by its ID. You can find the relationship
    between product names and IDs through the product search command.
    """
    global CLIENT, CONSOLE

    product = sc.product.read_with_versions(client=CLIENT, id=id, console=CONSOLE)

    product_extracted_version = product.versions[product.requested]

    CONSOLE.print(product_extracted_version.name, style="bold underline color(3)")
    CONSOLE.print(
        "\nVersions: "
        + helper.render_version_list(
            product.versions, product.current, product.requested
        )
    )
    CONSOLE.print(
        rich.markdown.Markdown(product_extracted_version.description.strip("\n"))
    )
    CONSOLE.print(product_extracted_version.metadata)
    CONSOLE.print(helper.render_source_list(product_extracted_version.sources, CACHE))
    CONSOLE.print("\n" + "Relationships" + "\n", style="bold color(2)")
    CONSOLE.print(
        "Collections: "
        + ", ".join(str(c) for c in product_extracted_version.collections)
    )
    if len(product_extracted_version.parent_of) > 0:
        CONSOLE.print("Children: " + ", ".join(product_extracted_version.parent_of))
    if len(product_extracted_version.child_of) > 0:
        CONSOLE.print("Parents: " + ", ".join(product_extracted_version.child_of))


@product_app.command("delete")
def product_delete(id: str):
    """
    Delete a product by its ID.
    """
    global CLIENT
    return sc.product.delete(client=CLIENT, id=id, console=CONSOLE)


@product_app.command("search")
def product_search(text: str):
    """
    Search for products by name.
    """
    global CLIENT, CONSOLE

    response = sc.product.search(client=CLIENT, text=text, console=CONSOLE)

    table = helper.render_product_metadata_list(response)

    CONSOLE.print(table)


@product_app.command("cache")
def product_cache(id: str):
    """
    Cache a product by its ID.
    """
    global CLIENT, CACHE

    response = sc.product.cache(client=CLIENT, cache=CACHE, id=id, console=CONSOLE)

    CONSOLE.print(f"Cached product {id} including {len(response)} files")


@product_app.command("uncache")
def product_uncache(id: str):
    """
    Uncache a product by its ID.
    """
    global CACHE

    sc.product.uncache(client=CLIENT, cache=CACHE, id=id, console=CONSOLE)

    CONSOLE.print(f"Uncached product {id}")


@product_app.command("edit")
def product_edit(id: str):
    """
    Edit a product by its ID.
    """
    global CLIENT

    edit_product(client=CLIENT, id=id)


@product_app.command("add-reader")
def product_add_reader(id: str, group: str):
    """
    Add a reader (by group name) to a product
    """

    global CLIENT
    updated_id = sc.product.product_add_reader(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Added {group} to {id} readers. New id is {updated_id}")


@product_app.command("remove-reader")
def product_remove_reader(id: str, group: str):
    """
    Remove a reader (by group name) from a product
    """

    global CLIENT
    updated_id = sc.product.product_remove_reader(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Removed {group} from {id} readers. New id is {updated_id}")


@product_app.command("add-writer")
def product_add_writer(id: str, group: str):
    """
    Add a writer (by group name) to a product
    """

    global CLIENT
    updated_id = sc.product.product_add_writer(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Added {group} to {id} writers. New id is {updated_id}")


@product_app.command("remove-writer")
def product_remove_writer(id: str, group: str):
    """
    Remove a writer (by group name) from a product
    """

    global CLIENT
    updated_id = sc.product.product_remove_writer(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Removed {group} from {id} writers. New id is {updated_id}")


@product_app.command("add-child")
def product_add_child(parent: str, child: str):
    """
    Add a child relationship between two products.
    """
    global CLIENT

    sc.relationships.add_child(
        client=CLIENT, parent=parent, child=child, console=CONSOLE
    )
    CONSOLE.print(f"Added {child} as child of {parent}")


@product_app.command("remove-child")
def product_remove_child(parent: str, child: str):
    """
    Remove a child relationship between two products.
    """
    global CLIENT

    sc.relationships.remove_child(
        client=CLIENT, parent=parent, child=child, console=CONSOLE
    )
    CONSOLE.print(f"Removed {child} as child of {parent}")


@collection_app.command("read")
def collection_read(id: str):
    """
    Read the information of a collection by its name.
    """
    global CLIENT, CONSOLE

    collection = sc.collections.read(client=CLIENT, id=id, console=CONSOLE)

    table = helper.render_product_metadata_list(collection.products)

    CONSOLE.print(collection.name + "\n", style="bold underline color(3)")
    CONSOLE.print(rich.markdown.Markdown(collection.description.strip("\n")))
    CONSOLE.print("\n")
    CONSOLE.print(table)


@collection_app.command("search")
def collection_search(name: str):
    """
    Search for collections by name.
    """
    global CLIENT, CONSOLE

    collections = sc.collections.search(client=CLIENT, name=name, console=CONSOLE)

    table = helper.render_collection_metadata_list(collections)

    CONSOLE.print(table)


@collection_app.command("cache")
def collection_cache(id: str):
    """
    Cache a collection by its name.
    """
    global CLIENT, CACHE

    response = sc.collections.cache(client=CLIENT, cache=CACHE, id=id, console=CONSOLE)

    CONSOLE.print(f"Cached collection {id} including {len(response)} files")


@collection_app.command("uncache")
def collection_uncache(id: str):
    """
    Uncache a collection by its name.
    """
    global CACHE

    sc.collections.uncache(client=CLIENT, cache=CACHE, id=id, console=CONSOLE)

    CONSOLE.print(f"Uncached collection {id}")


@collection_app.command("delete")
def collection_delete(id: str):
    """
    Delete a collection by its name.
    """
    global CLIENT

    sc.collections.delete(client=CLIENT, id=id, console=CONSOLE)

    CONSOLE.print(f"Deleted collection {id}")


@collection_app.command("add-product")
def collection_add_product(id: str, product_id: str):
    """
    Add a product to a collection.
    """
    global CLIENT
    updated_id = sc.collections.add(
        client=CLIENT, id=id, product=product_id, console=CONSOLE
    )
    CONSOLE.print(f"Added {product_id} to {id} collection. New ID is {updated_id}")


@collection_app.command("remove-product")
def collection_remove_product(id: str, product_id: str):
    """
    Remove a product from a collection.
    """
    global CLIENT
    updated_id = sc.collections.remove(
        client=CLIENT, id=id, product=product_id, console=CONSOLE
    )
    CONSOLE.print(f"Removed {product_id} from {id} collection. New ID is {updated_id}")


@collection_app.command("add-collection")
def collection_add_child(parent_id: str, child_id: str):
    """
    Add a sub-collection to a collection.
    """
    global CLIENT
    sc.relationships.add_child_collection(
        client=CLIENT, parent=parent_id, child=child_id, console=CONSOLE
    )
    CONSOLE.print(f"Added {child_id} to {parent_id} sub-collection")


@collection_app.command("remove-collection")
def collection_remove_child(parent_id: str, child_id: str):
    """
    Remove a sub-collection from a collection.
    """
    global CLIENT
    sc.relationships.remove_child_collection(
        client=CLIENT, parent=parent_id, child=child_id, console=CONSOLE
    )
    CONSOLE.print(f"Removed {child_id} from {parent_id} sub-collection")


@collection_app.command("add-reader")
def collection_add_reader(id: str, group: str):
    """
    Add a reader (by group name) to a collection.
    """
    global CLIENT
    updated_id = sc.collections.add_reader(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Added {group} to readers. Collection ID is {updated_id}")


@collection_app.command("remove-reader")
def collection_remove_reader(id: str, group: str):
    """
    Remove a reader (by group name) from a collection.
    """
    global CLIENT
    updated_id = sc.collections.remove_reader(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Removed {group} from readers. Collection ID is {updated_id}")


@collection_app.command("add-writer")
def collection_add_writer(id: str, group: str):
    """
    Add a writer (by group name) to a collection.
    """
    global CLIENT
    updated_id = sc.collections.add_writer(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Added {group} to writers. Collection ID is {updated_id}")


@collection_app.command("remove-writer")
def collection_remove_writer(id: str, group: str):
    """
    Remove a writer (by group name) from a collection.
    """
    global CLIENT
    updated_id = sc.collections.remove_writer(
        client=CLIENT, id=id, group=group, console=CONSOLE
    )
    CONSOLE.print(f"Removed {group} from writers. Collection ID is {updated_id}")


@cache_app.command("clear")
def cache_clear(uuid: str):
    """
    Clear the cache of a single file, labelled by its UUID (note that product IDs don't work here).
    """
    global CACHE

    for cache in CACHE.caches:
        if cache.writeable:
            sc.caching.clear_single(cache=cache, id=id, console=CONSOLE)
            CONSOLE.print(f"Cleared cache {cache.path} of {id}")


@cache_app.command("clear-all")
def cache_clear_all():
    """
    Clear all caches of all files.
    """
    global CACHE

    for cache in CACHE.caches:
        if cache.writeable:
            sc.caching.clear_all(cache=cache)
            CONSOLE.print(f"Cleared cache {cache.path}")


@dev_app.command("serve")
def dev_serve(
    port: Annotated[int, typer.Option(help="Port to run the server on")] = 8000,
):
    """
    Run a hippo development server, without spinning up dependencies (i.e. you
    will need to have mongo and minio running with appropriate environments set).
    """

    import uvicorn

    from hipposerve.api.app import app

    config = uvicorn.Config(
        app,
        port=port,
        reload=True,
        reload_dirs=["hipposerve/web", "hipposerve/web/templates"],
    )
    server = uvicorn.Server(config)

    try:
        server.run()
    except KeyboardInterrupt:
        exit(0)


@dev_app.command("run")
def dev_run(
    with_soauth: Annotated[
        bool,
        typer.Option(
            help="Run with SOAuth integration? If not, all requests are mock-authenticated"
        ),
    ] = False,
    port: Annotated[int, typer.Option(help="Port to run the server on")] = 8000,
):
    """
    Run a hippo development server, spinning up dependencies (i.e. we create
    temporary servers and set defaults for all variables that we can).
    """

    import os

    import uvicorn
    from testcontainers.minio import MinioContainer
    from testcontainers.mongodb import MongoDbContainer

    database_kwargs = {
        "username": "root",
        "password": "password",
        "port": 27017,
        "dbname": "hippo_test",
    }

    storage_kwargs = {}

    with MongoDbContainer(**database_kwargs) as database_container:
        with MinioContainer(**storage_kwargs) as storage_container:
            storage_config = storage_container.get_config()
            database_uri = database_container.get_connection_url()

            settings = {
                "mongo_uri": database_uri,
                "minio_url": storage_config["endpoint"],
                "minio_access": storage_config["access_key"],
                "minio_secret": storage_config["secret_key"],
                "title": "Test hippo",
                "description": "Test hippo Description",
                "debug": "yes",
                "add_cors": "yes",
                "web": "yes",
                "auth_system": "soauth" if with_soauth else "None",
            }

            os.environ.update(settings)

            # HIPPO must be imported _after_ updating settings.
            from hipposerve.api.app import app

            config = uvicorn.Config(
                app,
                port=port,
                reload=True,
                reload_dirs=["hipposerve/web", "hipposerve/web/templates"],
            )
            server = uvicorn.Server(config)

            try:
                server.run()
            except KeyboardInterrupt:
                exit(0)

    return


def main():
    settings = ClientSettings()

    global CLIENT, APP, CACHE, CONSOLE

    CLIENT = settings.client
    CACHE = settings.cache
    CONSOLE = rich.console.Console(quiet=not settings.verbose)

    APP()
