# ai-powered-personal-shopper
This is a ai-powered-personal-shopper

# AI-Powered Personal Shopper

This is a conversational AI application that helps users find personalized product recommendations using natural language input. Built with Chainlit, LangChain, OpenAI, and FastAPI.

## Features
- Chat with the AI using everyday language.
- Get tailored product recommendations.
- Works for various contexts (weddings, pool parties, casual wear, etc.).

## How to Run
### Backend
1. Navigate to the `backend` folder.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the backend: `uvicorn main:app --reload`.

### Frontend
1. Navigate to the `chainlit_app` folder.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the Chainlit app: `chainlit run app.py -w`.

## Example Use Case
- User Input: "I need a dark suit for a wedding dinner. Any recommendations?"
- AI Output: "A dark suit means navy, charcoal, or black. Here are some products:..."

