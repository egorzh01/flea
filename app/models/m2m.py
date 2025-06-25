from sqlalchemy import Column, ForeignKey, Table

from . import Base

documents_includes = Table(
    "documents_includes",
    Base.metadata,
    Column(
        "document_uid",
        ForeignKey(
            "documents.uid",
            ondelete="CASCADE",
            name="documents_includes_document_uid_fkey",
        ),
        primary_key=True,
    ),
    Column(
        "include_uid",
        ForeignKey(
            "includes.uid",
            ondelete="CASCADE",
            name="documents_includes_include_uid_fkey",
        ),
        primary_key=True,
    ),
)

images_includes = Table(
    "images_includes",
    Base.metadata,
    Column(
        "image_uid",
        ForeignKey(
            "images.uid",
            ondelete="CASCADE",
            name="images_includes_image_uid_fkey",
        ),
        primary_key=True,
    ),
    Column(
        "include_uid",
        ForeignKey(
            "includes.uid",
            ondelete="CASCADE",
            name="images_includes_include_uid_fkey",
        ),
        primary_key=True,
    ),
)

images_documents = Table(
    "images_documents",
    Base.metadata,
    Column(
        "image_uid",
        ForeignKey(
            "images.uid",
            ondelete="CASCADE",
            name="images_documents_image_uid_fkey",
        ),
        primary_key=True,
    ),
    Column(
        "document_uid",
        ForeignKey(
            "documents.uid",
            ondelete="CASCADE",
            name="images_documents_document_uid_fkey",
        ),
        primary_key=True,
    ),
)
