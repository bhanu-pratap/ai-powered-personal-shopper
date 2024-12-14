

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from langchain.prompts import PromptTemplate
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

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
    input_variables=["purpose", "product_group", "budget","style", "user_query"],
    template="""
You are a personal shopper helping users find the perfect outfit or product based on their needs.

Details:
- purpose: {purpose}
- Style Preferences: {style}
- Budget: {budget}
- product_group: product_group
- User's Query: "{user_query}"

Provide:
1. A brief recommendation.
2. Specific product suggestions (name, category, price, link).
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
def fetch_products(category):
    mock_products = [
        {"name": "Classic Black Suit", "category": "formal", "price": "$150", "url": "https://shorturl.at/oyo4e"},
        {"name": "Pool Party T-Shirt", "category": "casual", "price": "$25", "url": "https://shorturl.at/g8pui"},
    ]
    return [product for product in mock_products if category in product["category"]]

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
        products = fetch_products(category)
        
        return {"recommendation": response, "products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
