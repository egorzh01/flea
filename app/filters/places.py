from typing import Annotated

from fa_filter import Filter
from fastapi import Query
from pydantic import BeforeValidator

from app.models.place import Place


class PlacesFilter(Filter):
    parent_uid__eq: Annotated[
        int | None,
        BeforeValidator(lambda v: int(v) if v != "null" else None),
    ] = Query(
        default=None,
        title="Parent place ID",
    )

    class Settings(Filter.Settings):
        model = Place
        allowed_orders_by = [
            "name",
        ]
