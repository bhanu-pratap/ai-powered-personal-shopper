

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from langchain.prompts import PromptTemplate
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()
# Initialize FastAPI
app = FastAPI()

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize LangChain/OpenAI
llm = ChatOpenAI(
    model="gpt-3.5-turbo", 
    streaming=True,
    temperature=0.7
    )

# Define prompt template
prompt_template = PromptTemplate(
    input_variables=["purpose", "product_group", "budget","style", "user_query", "vendor"],
    template="""
You are a personal shopper helping users find the perfect outfit or product based on their needs.

Details:
- purpose: {purpose}
- Style Preferences: {style}
- Budget: {budget}
- product_group: product_group
- vendor: vendor
- User's Query: "{user_query}"

Provide:
    Create a 200-word recommendation including:
        Key product highlights and advantages
        Usage scenarios for target audience
        Specific product recommendations with reasoning
        Clear purchase links or call-to-action
"""
)

# Define request schema
class UserQuery(BaseModel):
    purpose: str
    product_group: str
    style: str
    budget: str
    user_query: str

# Mock product-fetching function
def fetch_products(input):
    url = "https://api.footwayplus.com/v1/inventory/search"

    querystring = input
    print(querystring, 'querystring')

    headers = {"X-API-KEY": "AIzaSyAXAQlouar4nC9w9qDE88KunaogEwSyboU"}
    products = []
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        products = json.loads(response.text)["items"]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    return [product for product in products ]

@app.post("/recommendation/")
async def recommend(query: UserQuery):
    try:
        # Construct prompt
        prompt = prompt_template.format(
            purpose=query.purpose,
            style=query.style,
            budget=query.budget,
            product_group=query.product_group,
            user_query=query.user_query
        )
        
        # Generate response using LangChain
        response = llm.predict(prompt)
        
        # Fetch mock products
        category = "formal" if "suit" in query.style.lower() else "casual"
        products = fetch_products(
            {
                "productGroup": query.product_group.capitalize(),
                "merchantId": '',
                "vendor": '',
                "department": '',
                "productType": '',
                "page": 1,
                "pageSize": ''
            }
        )
        
        return {"recommendation": response, "products": products}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
