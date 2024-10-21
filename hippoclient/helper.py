"""
Helpers for rendering cli elements.
"""

import rich

from hippoclient.caching import MultiCache
from hipposerve.api.models.relationships import (
    ReadCollectionProductResponse,
    ReadCollectionResponse,
)
from hipposerve.database import FileMetadata, ProductMetadata


def render_version_list(
    versions: list[str], current_version: str, requested_version: str
) -> str:
    """
    Render a list of versions to a bbcode string.

    Current version is bolded, requested version is green and underlined.
    """

    output = ""

    for version in versions:
        start = ""
        end = ""
        if version == current_version:
            start = f"[b]{start}"
            end = f"{end}[/b]"
        if version == requested_version:
            start = f"[u][color=green]{start}"
            end = f"{end}[/color][/u]"

        output += f"{start}{version}{end} "

    return output


def render_product_metadata_list(
    input: list[ProductMetadata | ReadCollectionProductResponse],
) -> rich.table.Table:
    """
    Render a list of product meadata into a rich table.
    """

    table = rich.table.Table("ID", "Name", "Version", "Uploaded")

    for product in input:
        table.add_row(
            str(product.id),
            product.name,
            product.version,
            product.uploaded.strftime("%Y-%m-%d %H:%M"),
        )

    return table


def render_collection_metadata_list(
    input: list[ReadCollectionResponse],
) -> rich.table.Table:
    """
    Render a list of collection metadata into a rich table.
    """

    table = rich.table.Table("ID", "Name", "Description")

    for collection in input:
        description = collection.description.strip("\n")

        # Truncate it if it's too long
        if len(description) > 512:
            description = description[:512] + "..."

        table.add_row(str(collection.id), collection.name, description)

    return table


def render_source_list(
    input: list[FileMetadata], cache: MultiCache | None = None
) -> rich.table.Table:
    """
    Render a list of source metadata into a rich table. If you provide
    a cache, we also query it to see if the files are cached.
    """

    table = rich.table.Table("Name", "Description", "UUID", "Size [B]", "Cached")

    for source in input:
        if cache is not None:
            try:
                cache.available(source.uuid)
                cached = "Yes"
            except FileNotFoundError:
                cached = "No"
        else:
            cached = "Unknown"

        table.add_row(
            source.name,
            source.description or "",
            source.uuid,
            str(source.size),
            cached,
        )

    return table