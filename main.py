from prompt import create_marketing_content, improve_marketing_content
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session
from PIL import Image, ImageDraw, ImageFont
import random
import io
import string
import json
import os

# Initialize the flask app
app = Flask(__name__)

generated_data = None
improved_data = None

# Define routes for the Flask app
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # Renders the form page

@app.route("/createnew", methods=["POST", "GET"])
def generate_content():
    if request.method == "GET":
        return redirect(url_for("index"))  # ✅ Redirects if accessed via GET

    global generated_data
    # Get form data from index.html
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
    "category": category,
    "brand": brand,
    "objective": objective,
    "medium": medium,
    "cta_button": cta_button,
    "offer": offer,
    "tone": tone,
    "specific_input": specific_input,
    "ab_testing": ab_testing,
    "result" : result
}

    return render_template("index.html", content=result, create_content =result,form_data_create =json.dumps(form_data or {}),
                          form_data=json.dumps(form_data or {}))  # Passes output to result.html

@app.route("/improveexisting", methods=["POST", "GET"])
def improve_content():
    if request.method == "GET":
        return redirect(url_for("index"))  # ✅ Redirects if accessed via GET
    global improved_data
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
    "category": category,
    "brand": brand,
    "medium": medium,
    "specific_input": specific_input,
    "ab_testing": ab_testing,
    "result":results,
    "existing_content":existing_content
     }
    
    return render_template("index.html", content=results, improve_content= results,     form_data=json.dumps(data_dict, ensure_ascii=False),
    form_data_improve=json.dumps(data_dict_i,ensure_ascii=False),
    existing_content = existing_content)  # Passes output to result.html

@app.route("/getdata", methods=["POST", "GET"])
def get_content():
    if request.method == "POST":
        requested_data = request.form.get("tabname", "")
        print(requested_data)
        print(generated_data)
        if requested_data == "CreateNew":
            print(generated_data)
            return jsonify({"generated_data": generated_data}), 200
        elif requested_data == "ImproveOld":
            print(improved_data)
            return jsonify({"improved_data": improved_data}), 200

app.secret_key = os.urandom(24)  # Generates a random secret key

# Function to load the font
def get_font():
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf")  # Path to bundled font
    try:
        return ImageFont.truetype(font_path, 36)  # Adjust size as needed
    except Exception as e:
        print(f"Font loading error: {e}")
        return ImageFont.load_default()

# Function to generate a CAPTCHA text
def generate_captcha_text(length=5):
    """Generate a random CAPTCHA text."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Function to create a CAPTCHA image
def create_captcha_image(text):
    """Create a CAPTCHA image from the given text."""
    width, height = 150, 60
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = get_font()
    
    # try:
    #     font = ImageFont.truetype("arial.ttf", 36)  # Ensure arial.ttf exists or change font
    # except:
    #     font = ImageFont.load_default()

    draw.text((20, 10), text, fill=(0, 0, 0), font=font)

    # Save image to a byte stream
    img_io = io.BytesIO()
    image.save(img_io, format="PNG")
    img_io.seek(0)
    return img_io


@app.route("/captcha", methods=["GET"])
def get_captcha():
    """Generate and return a CAPTCHA image."""
    captcha_text = generate_captcha_text()
    print("captcha_text",captcha_text)
    session["captcha"] = captcha_text  # Store CAPTCHA in session

    img_io = create_captcha_image(captcha_text)
    return send_file(img_io, mimetype="image/png")


# Function to validate the CAPTCHA
@app.route("/validate", methods=["POST"])
def validate_captcha():
    """Validate user input against the stored CAPTCHA."""
    user_input = request.json.get("captcha", "").strip()
    correct_captcha = session.get("captcha", "")
    
    print(correct_captcha,user_input)
    if user_input == correct_captcha:
        return jsonify({"message": "CAPTCHA validated successfully!", "success": True})
    else:
        return jsonify({"message": "Invalid CAPTCHA!", "success": False}), 400

@app.route("/captchaImprove", methods=["GET"])
def get_captchaImprove():
    """Generate and return a CAPTCHA image."""
    captcha_text = generate_captcha_text()
    print("captcha_text",captcha_text)
    session["captchaImprove"] = captcha_text  # Store fCAPTCHA in session

    img_io = create_captcha_image(captcha_text)
    return send_file(img_io, mimetype="image/png")

@app.route("/validateImprove", methods=["POST"])
def validate_captchaImprove():
    """Validate user input against the stored CAPTCHA."""
    user_input = request.json.get("captcha", "").strip()
    correct_captcha = session.get("captchaImprove", "")
    
    print(correct_captcha,user_input)
    if user_input == correct_captcha:
        return jsonify({"message": "CAPTCHA validated successfully!", "success": True})
    else:
        return jsonify({"message": "Invalid CAPTCHA!", "success": False}), 400
    
if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(debug=True)
    

