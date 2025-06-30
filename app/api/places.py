from typing import Annotated

from fastapi import (
    APIRouter,
    Query,
    status,
)

from app.database import DBSessionDep, safe_commit
from app.dependencies.auth import AuthDep
from app.filters.places import PlacesFilter
from app.schemas.place import PlaceCSchema, PlaceRLSchema, PlaceRSchema, PlaceUSchema
from app.services.places import PlacesService

router = APIRouter(
    tags=["places"],
)


@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[PlaceRLSchema],
)
async def get_places_list(
    db_session: DBSessionDep,
    auth: AuthDep,
    places_filter: Annotated[PlacesFilter, Query(default_factory=PlacesFilter)],
) -> list[PlaceRLSchema]:
    service = PlacesService(
        db_session=db_session,
        user_uid=auth.user_uid,
    )
    places_result = await service.get_places_list(places_filter)

    return [
        PlaceRLSchema.model_validate(place, from_attributes=True)
        async for place in places_result
    ]


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=PlaceRSchema,
)
async def create_place(
    schema: PlaceCSchema,
    db_session: DBSessionDep,
    auth: AuthDep,
) -> PlaceRSchema:
    service = PlacesService(
        db_session=db_session,
        user_uid=auth.user_uid,
    )
    async with safe_commit(db_session):
        place = await service.create_place(schema)
    return service.to_place_r_schema(place)


@router.get(
    path="/{place_uid}/",
    status_code=status.HTTP_200_OK,
    response_model=PlaceRSchema,
)
async def get_place(
    place_uid: int,
    db_session: DBSessionDep,
    auth: AuthDep,
) -> PlaceRSchema:
    service = PlacesService(
        db_session=db_session,
        user_uid=auth.user_uid,
    )
    place = await service.get_place(
        place_uid,
        join_parent=True,
    )
    return service.to_place_r_schema(place)


@router.patch(
    path="/{place_uid}/",
    status_code=status.HTTP_200_OK,
    response_model=PlaceRSchema,
)
async def update_place(
    place_uid: int,
    schema: PlaceUSchema,
    db_session: DBSessionDep,
    auth: AuthDep,
) -> PlaceRSchema:
    service = PlacesService(
        db_session=db_session,
        user_uid=auth.user_uid,
    )
    place = await service.get_place(
        place_uid,
        join_parent=True,
    )
    async with safe_commit(db_session):
        place = await service.update_place(
            place=place,
            schema=schema,
        )
    return service.to_place_r_schema(place)


@router.delete(
    path="/{place_uid}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_place(
    place_uid: int,
    db_session: DBSessionDep,
    auth: AuthDep,
) -> None:
    service = PlacesService(
        db_session=db_session,
        user_uid=auth.user_uid,
    )
    place = await service.get_place(place_uid)
    async with safe_commit(db_session):
        await service.delete_place(place)
