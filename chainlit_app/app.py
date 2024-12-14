import chainlit as cl
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import StrOutputParser
import os
import requests
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import json

load_dotenv()



BACKEND_URL = "http://localhost:8081/recommendation/"
extracted_data={}
# Initialize user session if it doesn't exist
extracted_data["purpose"] = "None"
extracted_data["product_group"] = "None"
extracted_data["style"] = "None"
extracted_data["budget"] = "None"
extracted_data["user_query"] = "None"


@cl.on_chat_start
async def on_chat_start():
    # Initialize LangChain OpenAI model
    llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7
    )

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """<START> You are a professional e-commerce personal shopping assistant. Please follow these steps strictly:
                    Information Gathering Phase:
                    Ask about user's specific shopping preferences (budget, style, purpose)
                    Confirm user's interested vendors, departments, or product categories
                    Note any special requirements or restrictions
                    Product Catalog Update (Must Execute):
                    Real-time update of product catalog based on user preferences
                    Display product names, prices, and stock status
                    List detailed specifications and features of relevant products
                    Marketing Content Creation (Must Execute):
                    Create a 300-word recommendation including:
                    Key product highlights and advantages
                    Usage scenarios for target audience
                    Specific product recommendations with reasoning
                    Clear purchase links or call-to-action
                    Page Theme Setting:
                    Select appropriate theme based on season/holiday/product type
                    Ensure visual elements align with product positioning
                    Please do not to repeat the same follow up question in the response once the user has provided its value e.g buget is 200 sek
                    Please do not bother user with follow up question if he mentions that does not know his preferneces 
                    Please provide confirmation after completing each step and wait for user feedback before proceeding to the next step.<END>
                    
                    Optimization Suggestions:

                    Added clear execution steps and sequence
                    Included mandatory execution markers
                    Set specific blog post word count requirement
                    Added confirmation mechanism
                    Detailed specific execution content for each step
                    
                    
                    """,
            ),
            (
                "human",
                "{question}"
            ),
        ]
    )

    # Create an LLMChain for managing conversation flow
    # chain = LLMChain(llm=llm, prompt=chat_prompt)
    chain = chat_prompt | llm 
    cl.user_session.set("chain", chain)
    await cl.Message(content= "I am CartPal! your Personal Shopper, What can I help you find today?").send()

@cl.on_message
async def main(message: cl.Message):
    global extracted_data

    # Retrieve the chain from the user's session (or initialize it if not present)
    chain = cl.user_session.get("chain")

    response = chain.invoke(input=message.content, callbacks=[cl.LangchainCallbackHandler()])
    data= await extract_parameters(message.content)

    # await cl.Message(content=data).send()
    dict_data = json.loads(data)

    # Filter keys with non-None values from 'data'
    non_none_data = {key: value for key, value in dict_data.items() if value is not None}
    extracted_data.update(non_none_data)
    # await cl.Message(content=extracted_data).send()

    # Check if 'product_group' and 'purpose' have non-None/empty values
    extracted_data.update(non_none_data)
    if extracted_data.get('product_group')!="None" and extracted_data.get('purpose') != "None":
        print("Both product_group and purpose have valid values.")
         # Build the user query
        user_query = {
            "purpose": extracted_data["purpose"],
            "product_group": extracted_data["product_group"],
            "style": extracted_data["style"],
            "budget": extracted_data["budget"],
            "user_query": f"I need help shopping for a {extracted_data['style']}."
        }

        # Send request to backend
        try:
            response = requests.post(BACKEND_URL, json=user_query).json()
            recommendation = response.get("recommendation", "No recommendation available.")
            products = response.get("products", [])

            # Format response
            # product_list = "\n".join([f"- {p['name']} ({p['category']}): {p['price']} [Link]({p['url']})" for p in products])
            product_list = "\n".join([f"- {p['name']} ({p['category']}): {p['price']} ![Image]({p['url']})" for p in products])
            await cl.Message(content=f"**Recommendation:** {recommendation}\n\n**Products:**\n{product_list}").send()
        except Exception as e:
             await cl.Message(content=f"Something went wrong: {str(e)}").send()

        # Reset session
        extracted_data = {}
        extracted_data["purpose"] = "None"
        extracted_data["product_group"] = "None"
        extracted_data["style"] = "None"
        extracted_data["budget"] = "None"
        extracted_data["user_query"] = "None"
        return
    else:
        print("Either product_group or purpose is missing a value.")
    
    # await cl.Message(content=f"Extracted Data: {extracted_data}").send()
    

    await cl.Message(content=response.content).send()


async def extract_parameters(user_input: str):
    # Define a prompt template to extract the necessary parameters
    prompt_template = """
    Extract the following parameters from the user's sentence:
    - budget (if any)
    - style (e.g., casual, formal)
    - purpose (e.g., wedding, work event)
    - product group (e.g., clothing, electronics)

    User input: "{input}"

    Output should be a dictionary with the following fields:
    - "budget": (the detected budget or "None" if not found)
    - "style": (the detected style or "None" if not found)
    - "purpose": (the detected purpose or "None" if not found)
    - "product_group": (the detected product group or "None" if not found)
    """

    # Create a prompt template using LangChain
    prompt = PromptTemplate(input_variables=["input"], template=prompt_template)
    llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7
    )
    chain = prompt | llm 
    response = chain.invoke(input=user_input)
    return response.content