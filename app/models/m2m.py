from sqlalchemy import Column, ForeignKey, Table

from . import Base

tags_items = Table(
    "tags_items",
    Base.metadata,
    Column(
        "tag_uid",
        ForeignKey(
            "tags.uid",
            ondelete="CASCADE",
            name="tags_items_tag_uid_fkey",
        ),
        primary_key=True,
    ),
    Column(
        "item_uid",
        ForeignKey(
            "items.uid",
            ondelete="CASCADE",
            name="tags_items_item_uid_fkey",
        ),
        primary_key=True,
    ),
)
