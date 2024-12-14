from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Define the models for the response
class FilterValue(BaseModel):
    name: str
    count: int

class MerchantValue(FilterValue):
    id: str

class FilterGroup(BaseModel):
    total: int
    values: list[FilterValue]

class MerchantGroup(BaseModel):
    total: int
    values: list[MerchantValue]

class AvailableFilters(BaseModel):
    totalItems: int
    merchants: MerchantGroup
    vendors: FilterGroup
    departments: FilterGroup
    productGroups: FilterGroup
    productTypes: FilterGroup

# Define the route to fetch available filters
@app.get("/availableFilters", response_model=AvailableFilters)
async def get_available_filters():
    try:
        # Fetch data from the external API
        response = requests.get(
            "https://api.footwayplus.com/v1/inventory/availableFilters",
            headers={
                "X-API-KEY": os.getenv("FOOTWAY_API_KEY"),
                "Content-Type": "application/json",
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error fetching filters: {response.text}",
            )

        # Parse and return the data
        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch filters: {str(e)}")
