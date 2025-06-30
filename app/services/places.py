from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, select, text
from sqlalchemy.ext.asyncio import AsyncScalarResult, AsyncSession
from sqlalchemy.orm import joinedload

from app.filters.places import PlacesFilter
from app.models.place import Place
from app.schemas.place import PlaceCSchema, PlaceRLSchema, PlaceRSchema, PlaceUSchema


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
        parent = None
        if schema.parent_uid:
            parent = await self.get_place(schema.parent_uid)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent place not found",
                )
        place = Place(
            name=schema.name,
            parent_uid=schema.parent_uid,
            owner_uid=self.user_uid,
            parent=parent,
        )
        self.db_session.add(place)
        return place

    async def get_places_list(
        self,
        places_filter: PlacesFilter | None = None,
    ) -> AsyncScalarResult[Place]:
        stmt = select(Place).filter(
            *self.get_places_acl_conditions(),
        )
        if places_filter:
            stmt = places_filter(stmt)
        return await self.db_session.stream_scalars(stmt)

    def get_places_acl_conditions(
        self,
    ) -> tuple[ColumnElement[bool]]:
        return (Place.owner_uid == self.user_uid,)

    async def get_place(
        self,
        place_uid: int,
        *,
        join_parent: bool = False,
    ) -> Place:
        stmt = select(Place).filter(
            Place.uid == place_uid,
            *self.get_places_acl_conditions(),
        )
        if join_parent:
            stmt = stmt.options(
                joinedload(Place.parent),
            )
        place = await self.db_session.scalar(stmt)
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
        schema: PlaceUSchema,
    ) -> Place:
        parent = place.parent
        if place.parent_uid != schema.parent_uid:
            if schema.parent_uid:
                parent = await self.get_place(schema.parent_uid)
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Parent place not found",
                    )
                parent_uids = await self.get_parent_uids(schema.parent_uid)
                if place.uid in parent_uids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cycle detected",
                    )
            else:
                parent = None
        place.parent = parent

        for attr, value in schema.model_dump(exclude_unset=True).items():
            setattr(place, attr, value)

        return place

    @staticmethod
    def to_place_r_schema(place: Place) -> PlaceRSchema:
        return PlaceRSchema(
            uid=place.uid,
            name=place.name,
            parent=PlaceRLSchema(
                uid=place.parent.uid,
                name=place.parent.name,
                parent_uid=place.parent.parent_uid,
            )
            if place.parent
            else None,
        )

    async def get_parent_uids(
        self,
        place_uid: int | None,
    ) -> set[int]:
        if place_uid is None:
            return set()
        cte = text(
            """
        WITH RECURSIVE lineplaces AS (
            SELECT uid, parent_uid
            FROM places
            WHERE uid = :place_uid

            UNION ALL

            SELECT f.uid, f.parent_uid
            FROM places f
            INNER JOIN lineplaces l ON l.parent_uid = f.uid
        )
        SELECT uid FROM lineplaces;
        """,
        ).bindparams(place_uid=place_uid)
        result = await self.db_session.execute(cte)
        return {row[0] for row in result}
