from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import requests
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
# Initialize FastAPI app
app = FastAPI()

# OpenAI initialization (example uses gpt-3.5-turbo)
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define response model for available filters
class FilterDescriptions(BaseModel):
    vendors: str = ""
    departments: str = ""
    productGroups: str = ""
    productTypes: str = ""

# Fetch available filters from the API
async def get_filter_descriptions():
    try:
        response = requests.get(
            "https://api.footwayplus.com/v1/inventory/availableFilters",
            headers={
                "X-API-KEY": os.getenv("FOOTWAY_API_KEY"),
                "Content-Type": "application/json",
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        return {
            "vendors": ", ".join([v["name"] for v in data.get("vendors", {}).get("values", [])]),
            "departments": ", ".join([d["name"] for d in data.get("departments", {}).get("values", [])]),
            "productGroups": ", ".join([pg["name"] for pg in data.get("productGroups", {}).get("values", [])]),
            "productTypes": ", ".join([pt["name"] for pt in data.get("productTypes", {}).get("values", [])]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filters: {str(e)}")

# Fetch products based on filters
@app.post("/fetch_vendor_products")
async def fetch_vendor_products(
    vendor: str = None,
    productName: str = None,
    department: str = None,
    productGroup: str = None,
    productType: str = None,
    page: int = 1,
    pageSize: int = 20,
):
    try:
        # Construct query parameters
        query_params = {
            "vendor": vendor,
            "productName": productName,
            "department": department,
            "productGroup": productGroup,
            "productType": productType,
            "page": page,
            "pageSize": pageSize,
        }

        # Remove empty parameters
        query_params = {key: value for key, value in query_params.items() if value}

        # Make API request
        response = requests.get(
            f"https://api.footwayplus.com/v1/inventory/search",
            headers={
                "X-API-KEY": os.getenv("FOOTWAY_API_KEY"),
                "Content-Type": "application/json",
            },
            params=query_params,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

# Fetch available filters
@app.get("/fetch_available_filters", response_model=FilterDescriptions)
async def fetch_available_filters():
    return await get_filter_descriptions()

# OpenAI API integration
@app.post("/chat_with_openai")
async def chat_with_openai(request: Request):
    try:
        body = await request.json()
        question = body.get("question", "")

        if not question:
            raise HTTPException(status_code=400, detail="Question is required.")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
        )

        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI: {str(e)}")





# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import os
# from langchain.prompts import PromptTemplate
# # from langchain.chat_models import ChatOpenAI
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv

# load_dotenv()
# # Initialize FastAPI
# app = FastAPI()

# # Load environment variables
# openai_api_key = os.getenv("OPENAI_API_KEY")

# # Initialize LangChain/OpenAI
# llm = ChatOpenAI(
#     model="gpt-3.5-turbo", 
#     streaming=True,
#     temperature=0.7
#     )

# # Define prompt template
# prompt_template = PromptTemplate(
#     input_variables=["occasion", "preferences", "budget", "user_query"],
#     template="""
# You are a personal shopper helping users find the perfect outfit or product based on their needs.

# Details:
# - Occasion: {occasion}
# - Style Preferences: {preferences}
# - Budget: {budget}
# - User's Query: "{user_query}"

# Provide:
# 1. A brief recommendation.
# 2. Specific product suggestions (name, category, price, link).
# """
# )

# # Define request schema
# class UserQuery(BaseModel):
#     occasion: str
#     preferences: str
#     budget: str
#     user_query: str

# # Mock product-fetching function
# def fetch_products(category):
#     mock_products = [
#         {"name": "Classic Black Suit", "category": "formal", "price": "$150", "url": "https://example.com/black-suit"},
#         {"name": "Pool Party T-Shirt", "category": "casual", "price": "$25", "url": "https://example.com/tshirt"},
#     ]
#     return [product for product in mock_products if category in product["category"]]

# @app.post("/recommendation/")
# async def recommend(query: UserQuery):
#     try:
#         # Construct prompt
#         prompt = prompt_template.format(
#             occasion=query.occasion,
#             preferences=query.preferences,
#             budget=query.budget,
#             user_query=query.user_query
#         )
        
#         # Generate response using LangChain
#         response = llm.predict(prompt)
        
#         # Fetch mock products
#         category = "formal" if "suit" in query.user_query.lower() else "casual"
#         products = fetch_products(category)
        
#         return {"recommendation": response, "products": products}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
