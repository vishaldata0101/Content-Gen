from prompt import create_marketing_content, improve_marketing_content
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import random
import io
import string
import json
import os
import time
import base64

improved_data = None
generated_data = None

# Initialize the flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random secret key

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # Renders the form page

@app.route("/createnew", methods=["POST", "GET"])
def generate_content():
    global generated_data
    if request.method == "GET":
        return redirect(url_for("index"))  # ✅ Redirects if accessed via GET
    
    category = request.form.get("category")
    brand = request.form.get("brand")
    objective = request.form.get("objective")
    medium = request.form.get("medium")
    cta_button = request.form.get("cta_button", None)
    offer = request.form.get("offer", None)
    tone = request.form.get("tone", None)
    specific_input = request.form.get("specific_input", None)
    ab_testing = request.form.get("ab_testing", "false") == "true"

    # Validate required fields
    if not all([category, brand, objective, medium]):
        return "Error: All required fields must be filled!", 400  # Bad request error

    # Call function to generate marketing content
    result = create_marketing_content(
        category, brand, objective, medium, cta_button, offer, tone, specific_input, ab_testing
    )

    form_data =  {
    "category": category,
    "brand": brand,
    "objective": objective,
    "medium": medium,
    "cta_button": cta_button,
    "offer": offer,
    "tone": tone,
    "specific_input": specific_input,
    "ab_testing": ab_testing
    }
    
    generated_data = {
        "category": request.form.get("category"),
        "brand": request.form.get("brand"),
        "objective": request.form.get("objective"),
        "medium": request.form.get("medium"),
        "cta_button": request.form.get("cta_button"),
        "offer": request.form.get("offer"),
        "tone": request.form.get("tone"),
        "specific_input": request.form.get("specific_input"),
        "ab_testing": request.form.get("ab_testing", "false") == "true",
        "result": result
    }

    return render_template("index.html", content=result, create_content=result, form_data_create=json.dumps(form_data or {}),
                          form_data=json.dumps(form_data or {}))

@app.route("/improveexisting", methods=["POST", "GET"])
def improve_content():
    global improved_data

    if request.method == "GET":
        return redirect(url_for("index"))  # ✅ Redirects if accessed via GET

    # Get form data from index.html
    existing_content = request.form.get("existing_content")
    category = request.form.get("category")
    brand = request.form.get("brand")
    medium = request.form.get("medium")
    specific_input = request.form.get("specific_input", None)
    ab_testing = request.form.get("ab_testing", "false") == "true"

    # Validate required fields
    if not all([existing_content, category, brand, medium]):
        return "Error: All required fields must be filled!", 400  # Bad request error
    
    # Call function to improve existing marketing content
    results = improve_marketing_content(existing_content, category, brand, medium, specific_input, ab_testing)
    
    data_dict = {
    "existing_content": existing_content,
    "category": category,
    "brand": brand,
    "medium": medium,
    "specific_input": specific_input,
    "ab_testing": ab_testing
    }

    data_dict_i = {
    "category": category,
    "brand": brand,
    "medium": medium,
    "specific_input": specific_input,
    "ab_testing": ab_testing
    }

    improved_data = {
        "existing_content": request.form.get("existing_content"),
        "category": request.form.get("category"),
        "brand": request.form.get("brand"),
        "medium": request.form.get("medium"),
        "specific_input": request.form.get("specific_input"),
        "ab_testing": request.form.get("ab_testing", "false") == "true",
        "result": results
    }
    
    return render_template("index.html", content=results, improve_content=results, 
                          form_data=json.dumps(data_dict, ensure_ascii=False),
                          form_data_improve=json.dumps(data_dict_i, ensure_ascii=False),
                          existing_content=existing_content)

@app.route("/getdata", methods=["POST", "GET"])
def get_content():
    global generated_data
    global improved_data
    
    if request.method == "POST":
        requested_data = request.form.get("tabname", "")

        if requested_data == "CreateNew":
            return jsonify({"generated_data": generated_data}), 200
        elif requested_data == "ImproveOld":
            generated_data = generated_data
            improved_data = improved_data
            if not improved_data:
                print("No improved data found, using generated data instead.")
                improved_data = generated_data.copy()
            else:
                # Check if other data is available and compare key-value pairs
                for key, value in generated_data.items():

                    if key in improved_data and improved_data[key] == value:
                        continue  # Keep the improved data
                    else:
                        if key != "result":
                            improved_data[key] = generated_data[key]

            # Now, improved_data contains the best available information

            improved_data['existing_content'] = generated_data['result']
            return jsonify({"improved_data": improved_data}), 200


# Function to load the font
def get_font():
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf")  # Path to bundled font
    try:
        return ImageFont.truetype(font_path, 36)  # Adjust size as needed
    except Exception as e:
        print(f"Font loading error: {e}")
        return ImageFont.load_default()

def generate_captcha_text(length=5):
    """Generate a random CAPTCHA text with uppercase, lowercase, and digits."""
    characters = string.ascii_letters + string.digits  # Uppercase, lowercase, and numbers
    return "".join(random.choices(characters, k=length))


def create_captcha_image(text):
    """Create a CAPTCHA image from the given text."""
    font = get_font()

    font = get_font()
    image = Image.new("RGB", (1, 1)) 
    draw = ImageDraw.Draw(image)

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

        # Add padding to avoid cutting
    width = text_width + 40  # Extra space to prevent cutoff
    height = max(60, text_height + 20)  # Ensure minimum height

    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill=(0, 0, 0), font=font)



    # Add some noise/lines to make it harder for bots
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(128, 128, 128), width=2)


    # Save image to a byte stream
    img_io = io.BytesIO()
    image.save(img_io, format="PNG")
    img_io.seek(0)
    return img_io

@app.get("/captcha")
def get_captcha():
    text = generate_captcha_text()  # Generate random text
    img_io = create_captcha_image(text)  # Generate image
    print("New Captcha",text)
    # Convert image to base64
    img_base64 = base64.b64encode(img_io.getvalue()).decode()

    return {"image": img_base64, "text": text}  # Send both image and text

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(debug=True)
