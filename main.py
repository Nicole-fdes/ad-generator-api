from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
import json

# 1. Initialize the App
app = FastAPI()

# 2. Initialize Groq Client
# We will use an environment variable for security on the server
# Fallback to the key you provided if running locally for testing
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)
MODEL_ID = "llama-3.1-8b-instant"

# 3. Define the Data Model (What the website sends us)
class AdRequest(BaseModel):
    platform: str
    objective: str
    brand: str
    product: str
    category: str
    price: str
    audience: str
    vibe: str
    highlights: str
    ingredients: str

# 4. The API Endpoint
@app.post("/generate-ads")
async def generate_ads(request: AdRequest):
    
    # Construct the prompt
    system_role = "You are a beauty marketing expert API. You output valid JSON only."
    
    user_prompt = f"""
    Generate 3 DISTINCT social media ad variations.
    
    CAMPAIGN SETTINGS:
    - Platform: {request.platform}
    - Objective: {request.objective}
    
    PRODUCT DETAILS:
    - Product: {request.product} ({request.brand})
    - Category: {request.category}
    - Price: {request.price}
    - Highlights: {request.highlights}
    - Ingredients: {request.ingredients}
    - Audience: {request.audience}
    - Vibe: {request.vibe}

    INSTRUCTIONS:
    - Return a JSON object with a key "variations" containing a list of 3 objects.
    - **BODY TEXT MUST BE UNDER 250 CHARACTERS.**
    - No bullet points.
    - Use beauty-specific emojis.
    
    JSON Schema:
    {{
        "variations": [
            {{
                "headline": "Headline 1",
                "body": "Body text...",
                "cta": "Call to action",
                "hashtags": ["#tag1", "#tag2"]
            }},
            {{
                "headline": "Headline 2",
                "body": "Body text...",
                "cta": "Call to action",
                "hashtags": ["#tag1", "#tag2"]
            }},
            {{
                "headline": "Headline 3",
                "body": "Body text...",
                "cta": "Call to action",
                "hashtags": ["#tag1", "#tag2"]
            }}
        ]
    }}
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_prompt}
            ],
            model=MODEL_ID,
            temperature=0.8,
            max_tokens=800,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON string from Groq into a real Python dictionary
        return json.loads(completion.choices[0].message.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Root endpoint just to check if server is running
@app.get("/")
def home():
    return {"status": "Ad Generator API is running 🚀"}
