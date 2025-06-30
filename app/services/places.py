from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, exists, select
from sqlalchemy.ext.asyncio import AsyncScalarResult, AsyncSession

from app.models.place import Place
from app.schemas.place import PlaceCSchema, PlaceRLSchema


class PlacesService:
    def __init__(
        self,
        db_session: AsyncSession,
        user_uid: int,
    ):
        self.db_session = db_session
        self.user_uid = user_uid

    async def create_place(
        self,
        schema: PlaceCSchema,
    ) -> Place:
        if schema.parent_uid and await self.db_session.scalar(
            exists().filter(
                Place.uid == schema.parent_uid,
                Place.owner_uid == self.user_uid,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent place not found",
            )
        if await self.db_session.scalar(
            exists().filter(
                Place.name == schema.name,
                Place.parent_uid == schema.parent_uid,
                Place.owner_uid == self.user_uid,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Place with this name and parent already exists",
            )

        place = Place(
            name=schema.name,
            parent_uid=schema.parent_uid,
            owner_uid=self.user_uid,
        )
        self.db_session.add(place)
        return place

    async def get_places_list(
        self,
    ) -> AsyncScalarResult[Place]:
        return await self.db_session.stream_scalars(
            select(Place).filter(
                *self.get_places_acl_conditions(),
            )
        )

    def get_places_acl_conditions(
        self,
    ) -> tuple[ColumnElement[bool]]:
        return (Place.owner_uid == self.user_uid,)

    async def get_place(
        self,
        place_uid: int,
    ) -> Place:
        place = await self.db_session.scalar(
            select(Place).filter(
                Place.uid == place_uid,
                *self.get_places_acl_conditions(),
            )
        )
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found",
            )
        return place

    async def delete_place(
        self,
        place: Place,
    ) -> None:
        await self.db_session.delete(place)

    async def update_place(
        self,
        place: Place,
        schema: PlaceCSchema,
    ) -> Place:
        parent_changed = place.parent_uid != schema.parent_uid
        if parent_changed:
            if schema.parent_uid:
                parent_exists = await self.db_session.scalar(
                    select(
                        exists().where(
                            Place.uid == schema.parent_uid,
                            Place.owner_uid == self.user_uid,
                        )
                    )
                )
                if not parent_exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Parent place not found",
                    )
            place.parent_uid = schema.parent_uid

        if place.name != schema.name or parent_changed:
            duplicate_exists = await self.db_session.scalar(
                select(
                    exists().where(
                        Place.name == schema.name,
                        Place.parent_uid == place.parent_uid,
                        Place.owner_uid == self.user_uid,
                    )
                )
            )
            if duplicate_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Place with this name already exists",
                )
            place.name = schema.name

        return place

    @staticmethod
    def to_place_rl_schema(place: Place) -> PlaceRLSchema:
        return PlaceRLSchema(
            uid=place.uid,
            name=place.name,
            parent_uid=place.parent_uid,
        )
