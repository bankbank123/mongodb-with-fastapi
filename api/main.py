from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import item, customers
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],  # Update with your React app's origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],  # You can refine this to allow specific headers if needed
)
app.include_router(item.router)
app.include_router(customers.router)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)