from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.item import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])

# In-memory storage for demo purposes
items_db: dict[int, Item] = {}
current_id = 0


@router.get(
    "/",
    response_model=list[Item],
    summary="List all items",
    description="Retrieve a list of all items in the system. Returns an empty list if no items exist.",
    response_description="List of items",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Widget",
                            "description": "A high-quality widget",
                            "price": 29.99,
                        },
                        {
                            "id": 2,
                            "name": "Gadget",
                            "description": "An innovative gadget",
                            "price": 49.99,
                        },
                    ]
                }
            },
        }
    },
)
def get_items():
    """
    Retrieve all items.

    Returns a list of all items currently stored in the system.
    The list may be empty if no items have been created yet.
    """
    return list(items_db.values())


@router.get(
    "/{item_id}",
    response_model=Item,
    summary="Get an item by ID",
    description="Retrieve a specific item by its unique identifier.",
    response_description="The requested item",
    responses={
        200: {
            "description": "Item found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Widget",
                        "description": "A high-quality widget",
                        "price": 29.99,
                    }
                }
            },
        },
        404: {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Item not found"}
                }
            },
        },
    },
)
def get_item(
    item_id: int = Path(
        ...,
        description="The unique identifier of the item to retrieve",
        gt=0,
        example=1,
    ),
):
    """
    Retrieve a specific item by ID.

    - **item_id**: The unique identifier of the item
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@router.post(
    "/",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Create a new item with the provided data. The item will be assigned a unique ID.",
    response_description="The created item",
    responses={
        201: {
            "description": "Item created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Widget",
                        "description": "A high-quality widget",
                        "price": 29.99,
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "price"],
                                "msg": "Input should be greater than 0",
                                "type": "greater_than",
                            }
                        ]
                    }
                }
            },
        },
    },
)
def create_item(item: ItemCreate):
    """
    Create a new item.

    - **name**: The name of the item (required)
    - **description**: Optional description of the item
    - **price**: The price in USD (must be greater than 0)
    """
    global current_id
    current_id += 1
    new_item = Item(id=current_id, **item.model_dump())
    items_db[current_id] = new_item
    return new_item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    description="Delete an item by its unique identifier. This action cannot be undone.",
    responses={
        204: {
            "description": "Item deleted successfully",
        },
        404: {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Item not found"}
                }
            },
        },
    },
)
def delete_item(
    item_id: int = Path(
        ...,
        description="The unique identifier of the item to delete",
        gt=0,
        example=1,
    ),
):
    """
    Delete an item by ID.

    - **item_id**: The unique identifier of the item to delete
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
