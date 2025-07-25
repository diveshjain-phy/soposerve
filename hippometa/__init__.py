"""
Metadata specification for the Simons Observatory Post Office.

This package provides pydantic models describing all of the metadata
types that the Post Office can handle, and potentially some
utility functions for automatically filling out the structures with
data.

Each metadata type can provide utility functions as a class method.
Each metadata type must inherit from the BaseMetadata type defined here.
Each metadata type must have a unique `metadata_type` field which is a
string used as a discriminator.
Each metadata type must be added to the below ALL_METADATA and
ALL_METADATA_TYPE lists.
"""

from typing import Annotated, Union

from pydantic import Field

from hippometa.archive import ArchiveMetadata
from hippometa.beam import BeamMetadata
from hippometa.cameras import CameraMetadata
from hippometa.catalog import CatalogMetadata
from hippometa.mapset import MapSet
from hippometa.numeric import NumericMetadata
from hippometa.simple import SimpleMetadata

ALL_METADATA_TYPE = Annotated[
    Union[
        ArchiveMetadata,
        BeamMetadata,
        MapSet,
        CatalogMetadata,
        NumericMetadata,
        SimpleMetadata,
        CameraMetadata,
        None,
    ],
    Field(discriminator="metadata_type"),
]

ALL_METADATA = {
    x.model_fields["metadata_type"].default: x
    for x in [
        ArchiveMetadata,
        BeamMetadata,
        MapSet,
        CatalogMetadata,
        NumericMetadata,
        SimpleMetadata,
        CameraMetadata,
    ]
}
