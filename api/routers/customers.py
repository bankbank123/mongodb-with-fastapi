from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import motor.motor_asyncio as motor

router = APIRouter(
    prefix="/api",
    tags=["customers"],
    responses={404: {"message": "Not Found"}}
)

MONGODB_URL = "mongodb+srv://admin:admin@items.g8jml3w.mongodb.net/"
client = motor.AsyncIOMotorClient(MONGODB_URL)
db = client["warehouse_database"]
collection = db["customers"]


class ItemDT0(BaseModel):
    _id: int
    employee_id: str
    first_name: str
    last_name: str
    age: int
    email: str
    country: str
    favorite_color: str
    job_title: str
    salary: int

class ItemCreateDT0(BaseModel):
    _id: int    
    first_name: str
    last_name: str
    age: int
    email: str
    country: str
    favorite_color: str
    job_title: str
    salary: int

class ItemUpdateDT0(BaseModel):
    _id: int
    employee_id: str
    first_name: str = Field(None)
    last_name: str = Field(None)
    age: int = Field(None)
    email: str = Field(None)
    country: str = Field(None)
    favorite_color: str = Field(None)
    job_title: str = Field(None)
    salary: int = Field(None)

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

@router.post("/customers/", tags=["customers"])
async def create_item(item: ItemCreateDT0):
    try:
        customer_id = await get_last()
        
        customer_id = customer_id + 1
        print(f"Generated customer ID: {customer_id}")
        
        customers_data = item.dict()
        customers_data["_id"] = customer_id
        print(f"customer data to insert: {customer_id}")
        
        text_ID = "UID"
        customers_UID = str(customer_id)
        while len(customers_UID) <= 6:
            customers_UID = "0" + customers_UID
        concat_text = text_ID + customers_UID
        
        customers_data["employee_id"] = concat_text
        result = await collection.insert_one(customers_data)
        print(f"Insert result: {result}")
        return {"message": "customers created successfully"}
    except Exception as e:
        print(f"Error creating item: {str(e)}")
        return {"message": "Error creating item"}

@router.get("/customers/", response_model=list[ItemDT0], tags=["customers"])
async def get_all_items():
    customers = await collection.find().to_list(length=None)
    return customers

@router.get("/customers/{customers_id}", tags=["customers"])
async def get_item_by_id(customers_id: int):
    customers = await collection.find_one({"_id": customers_id})
    if customers:
        return customers
    else:
        return {"message": "customers not found"}
    
@router.get("/customers/search/{customers_id}", tags=["customers"])
async def get_item_by_UID(customers_id: str):
    customers = await collection.find_one({"employee_id": customers_id})
    if customers:
        return customers
    else:
        raise HTTPException(status_code=404, detail="customer not found")
    
@router.put("/customers/{customers_id}", tags=["customers"])
async def update_item(customers_id: int, updated_customers: ItemUpdateDT0):
    await collection.update_one({"_id": customers_id}, {"$set": updated_customers.dict()})
    return {"message": "customers updated successfully"}


@router.get("/customers/edit/{customers_employee_id}", tags=["customers"])
async def get_item_by_emoployee(customers_id: str):
    customers = await collection.find_one({"employee_id": customers_id})
    if customers:
        return customers
    else:
        return {"message": "customers not found"}

@router.delete("/customers/{customers_id}", tags=["customers"])
async def delete_item(customers_id: str):
    try:
        item = await collection.find_one({"employee_id": customers_id})
        if item:
            await collection.delete_one({"employee_id": customers_id})
            return {"message": "Item deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))