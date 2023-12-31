from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from pymongo import MongoClient
import shortuuid
from fastapi import Request


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
#latest aur latest
class LinkRequest(BaseModel):
    url: str
    cta_message: str
    selected_component: str  # Add selected_component field
    selected_alignment: str  # Add selected_component field
    visit_count: int = 0

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
        "selected_component": link_request.selected_component,
        "selected_alignment": link_request.selected_alignment,
        "visit_count":0,
    }
    links_collection.insert_one(link_data)

    return {"short_code": short_code}

@app.get("/track-visit/{short_code}")
async def track_visit(short_code: str, request: Request):
    # Find the link data in MongoDB based on the short code
    link_data = links_collection.find_one({"short_code": short_code})

    if not link_data:
        raise HTTPException(status_code=404, detail="Shortened link not found")

    # Increment the visit count and update the link data in the database
    updated_visit_count = link_data.get("visit_count", 0) + 1

    # Get the user's IP address from the request
    user_ip = request.client.host

    # Store the IP address along with other tracking data
    link_data["visit_count"] = updated_visit_count
    link_data["user_ip"] = user_ip

    # Update the link data in MongoDB
    links_collection.update_one({"short_code": short_code}, {"$set": link_data})

    # Log the visit, the user's IP address, and the updated visit count
    print(f"Visited {short_code}. User IP: {user_ip}. Visit count: {updated_visit_count}")

    # Redirect the user to the original URL
    return RedirectResponse(url=link_data["url"])



@app.get("/{domain_path}/{short_code}", response_class=HTMLResponse)
async def get_website_with_overlay(domain_path: str, short_code: str):
    # Decode the domain path from the URL
    domain_path = domain_path.replace("_", "/")  # Convert underscores back to slashes

    # Retrieve the original URL, overlay message, and selected component based on the short code from MongoDB
    link_data = links_collection.find_one({"short_code": short_code})

    if not link_data:
        raise HTTPException(status_code=404, detail="Shortened link not found")

    url = link_data["url"]
    selected_component = link_data.get("selected_component", "Component1")  # Default to Component1 if not found
    selected_alignment = link_data.get("selected_alignment", "bottom left")  # Default to Component1 if not found

    # Define the image URL and style
    image_url1 = "https://res.cloudinary.com/dxtzjwkhk/image/upload/v1696601029/krisna/component-1_e0ejvn.png"
    image_url2 = "https://res.cloudinary.com/dxtzjwkhk/image/upload/v1696601030/krisna/component-2_cwgff3.png"
    image_url3 = "https://res.cloudinary.com/dxtzjwkhk/image/upload/v1696601029/krisna/component-3_vmhv6c.png"
    image_url4 = "https://res.cloudinary.com/dxtzjwkhk/image/upload/v1696601028/krisna/component-4_l9wuux.png"
    image_url5 = "https://res.cloudinary.com/dxtzjwkhk/image/upload/v1696601029/krisna/component-5_rgkqid.png"
    image_url6 = "https://res.cloudinary.com/dxtzjwkhk/image/upload/v1696601029/krisna/component-6_trujdm.png"

    # Determine the component to render based on selected_component
    if selected_alignment == "bottom left":
        image_style = "width: 250px; position: absolute; bottom: 1%; left: 1%;"
    elif selected_alignment == "bottom center":
        image_style = "width: 250px; position: absolute; bottom: 1%; left: 40%;"
    elif selected_alignment == "bottom right":
        image_style = "width: 250px; position: absolute; bottom: 1%; right: 1%;"

    component_to_render = None
    if selected_component == "Component1":
        component_to_render = f"<img src='{image_url1}' style='{image_style}' alt='Overlay Image'>"
    elif selected_component == "Component2":
        component_to_render = f"<img src='{image_url2}' style='{image_style}' alt='Overlay Image'>"
    elif selected_component == "Component3":
        component_to_render = f"<img src='{image_url3}' style='{image_style}' alt='Overlay Image'>"
    elif selected_component == "Component4":
        component_to_render = f"<img src='{image_url4}' style='{image_style}' alt='Overlay Image'>"
    elif selected_component == "Component5":
        component_to_render = f"<img src='{image_url5}' style='{image_style}' alt='Overlay Image'>"
    elif selected_component == "Component6":
        component_to_render = f"<img src='{image_url6}' style='{image_style}' alt='Overlay Image'>"

    # Generate the HTML content with the embedded iframe and selected component
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generated Website with Overlay</title>
    </head>
    <body style="padding: 0; margin: 0;">
        <iframe src="{url}" width="100%" height="900px" frameborder="0"></iframe>
        {component_to_render}
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)



@app.get("/track-visit/{short_code}")
async def track_visit(short_code: str, request: Request):
    # Find the link data in MongoDB based on the short code
    link_data = links_collection.find_one({"short_code": short_code})

    if not link_data:
        raise HTTPException(status_code=404, detail="Shortened link not found")

    # Increment the visit count and update the link data in the database
    updated_visit_count = link_data.get("visit_count", 0) + 1

    # Get the user's IP address from the request
    user_ip = request.client.host

    # Store the IP address along with other tracking data
    link_data["visit_count"] = updated_visit_count
    link_data["user_ip"] = user_ip

    # Update the link data in MongoDB
    links_collection.update_one({"short_code": short_code}, {"$set": link_data})

    # Log the visit, the user's IP address, and the updated visit count
    print(f"Visited {short_code}. User IP: {user_ip}. Visit count: {updated_visit_count}")

    # Redirect the user to the original URL
    return RedirectResponse(url=link_data["url"])


