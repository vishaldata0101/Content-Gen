from prompt import create_marketing_content, improve_marketing_content
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

# Initialize the flask app
app = Flask(__name__)

# Define routes for the Flask app
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # Renders the form page

@app.route("/createnew", methods=["POST", "GET"])
def generate_content():
    if request.method == "GET":
        return redirect(url_for("index"))  # ✅ Redirects if accessed via GET

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

    return render_template("index.html", content=result, create_content =result,form_data_create =json.dumps(form_data or {}),
                          form_data=json.dumps(form_data or {}))  # Passes output to result.html

@app.route("/improveexisting", methods=["POST", "GET"])
def improve_content():
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

    return render_template("index.html", content=results, improve_content= results,     form_data=json.dumps(data_dict, ensure_ascii=False),
    form_data_improve=json.dumps(data_dict_i,ensure_ascii=False),
    existing_content = existing_content)  # Passes output to result.html

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(debug=True)
    

