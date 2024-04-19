from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import motor.motor_asyncio as motor
from datetime import date


router = APIRouter(
    prefix="/api",
    tags=["item"],
    responses={404: {"message": "Not Found"}}
)

MONGODB_URL = "mongodb+srv://admin:admin@items.g8jml3w.mongodb.net/"
client = motor.AsyncIOMotorClient(MONGODB_URL)
db = client["warehouse_database"]
collection = db["store"]
date_today = date.today()

class ItemDT0(BaseModel):
    _id: int
    product_name: str
    brand: str
    price: float
    quantity: int
    description: str
    manufacturer: str   
    date_added: str
    is_available: bool

class ItemCreateDT0(BaseModel):
    _id: int
    product_name: str
    brand: str
    price: float
    quantity: int
    description: str
    manufacturer: str   
    date_added: str = date_today.strftime("%d/%m/%Y")
    is_available: bool

class ItemUpdateDT0(BaseModel):
    _id: int
    product_name: str = Field(None)
    brand: str = Field(None)
    price: float = Field(None)
    quantity: int = Field(None)
    description: str = Field(None)
    manufacturer: str = Field(None)
    date_added: str = Field(None)
    is_available: bool = Field(None)
    
async def get_last():
    try:
        # Sort by the '_id' field in descending order and limit the result to 1 document
        last_item = await collection.find_one(sort=[('_id', -1)], projection={'_id': 1})

        if last_item:
            # Return the value of the '_id' field
            item_id = last_item.get('_id')
            if item_id is not None:
                return item_id
            else:
                raise HTTPException(status_code=404, detail="'_id' field not found in the item")
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items/", tags=["item"])
async def create_item(item: ItemCreateDT0):
    try:
        item_id = await get_last()
        item_id = item_id + 1
        print(f"Generated item ID: {item_id}")
        
        item_data = item.dict()
        item_data["_id"] = item_id
        print(f"Item data to insert: {item_data}")

        result = await collection.insert_one(item_data)
        print(f"Insert result: {result}")

        return {"message": "Item created successfully"}
    except Exception as e:
        print(f"Error creating item: {str(e)}")
        return {"message": "Error creating item"}

@router.get("/items/", response_model=list[ItemDT0], tags=["item"])
async def get_all_items():
    items = await collection.find().to_list(length=None)
    return items


@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await collection.find_one({"_id": item_id})
    if item:
        return item
    else:
        return {"message": "Item not found"}
    
@router.put("/items/{item_id}", tags=["item"])
async def update_item(item_id: int, updated_item: ItemUpdateDT0):
    await collection.update_one({"_id": item_id}, {"$set": updated_item.dict()})
    return {"message": "Item updated successfully"}

@router.delete("/items/{item_id}", tags=["item"])
async def delete_item(item_id: int):
    try:
        item = await collection.find_one({"_id": item_id})
        if item:
            await collection.delete_one({"_id": item_id})
            return {"message": "Item deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))