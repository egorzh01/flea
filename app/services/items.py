from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, exists, select
from sqlalchemy.ext.asyncio import AsyncScalarResult, AsyncSession

from app.models.category import Category
from app.models.item import Item
from app.models.place import Place
from app.models.unit import Unit
from app.schemas.item import ItemCSchema, ItemUSchema


class ItemsService:
    def __init__(
        self,
        db_session: AsyncSession,
        user_uid: int,
    ):
        self.db_session = db_session
        self.user_uid = user_uid

    def get_items_acl_conditions(self) -> tuple[ColumnElement[bool]]:
        return (Item.owner_uid == self.user_uid,)

    async def get_items_list(self) -> AsyncScalarResult[Item]:
        return await self.db_session.stream_scalars(
            select(Item).filter(
                *self.get_items_acl_conditions(),
            )
        )

    async def get_item(self, item_uid: int) -> Item:
        item = await self.db_session.scalar(
            select(Item).filter(
                Item.uid == item_uid,
                *self.get_items_acl_conditions(),
            )
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return item

    async def create_item(self, schema: ItemCSchema) -> Item:
        if schema.unit_uid:
            unit_exists = await self.db_session.scalar(
                select(
                    exists().where(
                        Unit.uid == schema.unit_uid,
                    )
                )
            )
            if not unit_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unit not found",
                )
        if schema.category_uid:
            category_exists = await self.db_session.scalar(
                select(
                    exists().where(
                        Category.uid == schema.category_uid,
                    )
                )
            )
            if not category_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found",
                )
        if schema.place_uid:
            place_exists = await self.db_session.scalar(
                select(
                    exists().where(
                        Place.uid == schema.place_uid,
                        Place.owner_uid == self.user_uid,
                    )
                )
            )
            if not place_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Place not found",
                )
        item = Item(
            name=schema.name,
            description=schema.description,
            price=schema.price,
            currency_code=schema.currency_code,
            quantity=schema.quantity,
            owner_uid=self.user_uid,
            unit_uid=schema.unit_uid,
            category_uid=schema.category_uid,
            place_uid=schema.place_uid,
            is_public=schema.is_public,
        )
        self.db_session.add(item)
        return item

    async def delete_item(self, item: Item) -> None:
        await self.db_session.delete(item)

    async def update_item(
        self,
        item: Item,
        schema: ItemUSchema,
    ) -> Item:
        upd = schema.model_dump(exclude_unset=True)

        if schema.unit_uid:
            unit_exists = await self.db_session.scalar(
                select(
                    exists().where(
                        Unit.uid == schema.unit_uid,
                    )
                )
            )
            if not unit_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unit not found",
                )
        if schema.category_uid:
            category_exists = await self.db_session.scalar(
                select(
                    exists().where(
                        Category.uid == schema.category_uid,
                    )
                )
            )
            if not category_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found",
                )
        if schema.place_uid:
            place_exists = await self.db_session.scalar(
                select(
                    exists().where(
                        Place.uid == schema.place_uid,
                        Place.owner_uid == self.user_uid,
                    )
                )
            )
            if not place_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Place not found",
                )

        for key, value in upd.items():
            setattr(item, key, value)

        return item
