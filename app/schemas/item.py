from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The name of the item",
        json_schema_extra={"example": "Widget"},
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of the item",
        json_schema_extra={"example": "A high-quality widget for everyday use"},
    )
    price: float = Field(
        ...,
        gt=0,
        description="The price of the item in USD",
        json_schema_extra={"example": 29.99},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Widget",
                    "description": "A high-quality widget for everyday use",
                    "price": 29.99,
                }
            ]
        }
    }


class Item(ItemCreate):
    """Schema for an item with its ID."""

    id: int = Field(
        ...,
        description="The unique identifier of the item",
        json_schema_extra={"example": 1},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Widget",
                    "description": "A high-quality widget for everyday use",
                    "price": 29.99,
                }
            ]
        }
    }
