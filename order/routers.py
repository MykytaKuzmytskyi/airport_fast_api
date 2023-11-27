from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from order import schemas, crud
from dependencies import get_db
from user import auth
from user.models import User

router = APIRouter()


@router.post(
    "/order",
    tags=["Order"],
    status_code=status.HTTP_201_CREATED,
)
async def order_create(
    db: AsyncSession = Depends(get_db),
    order_data: schemas.OrderCreateSchema | None = None,
    user: User = Depends(auth.current_user),
):
    return await crud.create_order(db=db, order_data=order_data, user=user)
