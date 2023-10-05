from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pymongo import MongoClient
import shortuuid

app = FastAPI()

# Configure CORS policy to allow requests from your React app's origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://websiteconverter.netlify.app"],  # Replace with the actual origin of your React app
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# MongoDB setup
client = MongoClient("mongodb://musu:Musu17Hanu@ac-qekgspq-shard-00-00.hrsqgub.mongodb.net:27017,ac-qekgspq-shard-00-01.hrsqgub.mongodb.net:27017,ac-qekgspq-shard-00-02.hrsqgub.mongodb.net:27017/?replicaSet=atlas-gwgnya-shard-0&ssl=true&authSource=admin")
db = client["cta_overlay_db"]
links_collection = db["links"]

class LinkRequest(BaseModel):
    url: str
    cta_message: str
    selected_component: str  # Add selected_component field

class ShortenedLink(BaseModel):
    short_code: str

@app.post("/generate-link/", response_model=ShortenedLink)
async def generate_link(link_request: LinkRequest):
    # Generate a unique short code for the link
    short_code = shortuuid.uuid()

    # Store the link_request.url, link_request.cta_message, link_request.selected_component, and short_code in MongoDB
    link_data = {
        "short_code": short_code,
        "url": link_request.url,
        "cta_message": link_request.cta_message,
        "selected_component": link_request.selected_component,  # Store selected component
    }
    links_collection.insert_one(link_data)

    return {"short_code": short_code}

@app.get("/{short_code}", response_class=HTMLResponse)
async def get_website_with_overlay(short_code: str):
    # Retrieve the original URL, overlay message, and selected component based on the short code from MongoDB
    link_data = links_collection.find_one({"short_code": short_code})

    if not link_data:
        raise HTTPException(status_code=404, detail="Shortened link not found")

    url = link_data["url"]
    selected_component = link_data.get("selected_component", "Component1")  # Default to Component1 if not found

    # Define the image URL and style
    image_url = "https://i.postimg.cc/d0KKBbQS/catax-logo.jpg"  # Replace with the actual URL of your image
    image_style = "border-radius: 50%; border: 4px solid black; width: 100px; height: 100px; position: absolute; bottom: 10px; left: 10px;"

    # Determine the component to render based on selected_component
    component_to_render = None
    if selected_component == "Component1":
        component_to_render = "<h2>Component 1 Content</h2>"
    elif selected_component == "Component2":
        component_to_render = "<h2>Component 2 Content</h2>"
    elif selected_component == "Component3":
        component_to_render = "<h2>Component 3 Content</h2>"
    elif selected_component == "Component4":
        component_to_render = "<h2>Component 4 Content</h2>"

    # Generate the HTML content with the embedded iframe and selected component
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generated Website with Overlay</title>
    </head>
    <body style="padding: 0; margin: 0;">
        <iframe src="{url}" width="100%" height="1000px" frameborder="0"></iframe>
        <img src="{image_url}" style="{image_style}" alt="Overlay Image">
        {component_to_render}
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
