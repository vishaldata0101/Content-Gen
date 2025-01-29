from flask import Flask, render_template, request
import openai
import config  # Import the configuration file

app = Flask(__name__)

# Categories and Medium options for dropdowns
CATEGORIES = [
                "None", 
                "Fashion & Apparel",
                "Beauty & Personal Care",
                "Health & Wellness",
                "Food & Beverages",
                "Tech & Gadgets",
                "Financial Services & Insurance",
                "Entertainment & Media",
                "Arts & Crafts",
                "Automotive & Accessories"
                ]

MEDIUMS = ["None", "SMS", "WhatsApp", "Email"]


TONES = [
            "None", "Anticipation", "Joy", "Trust", "Fear of Missing Out(FOMO)", "Surprise", "Excitement", 
            "Curiosity",  "Calmness", "Security", "Kindness", "Admiration",  "Thankfulness", 
            "Hope", "Reliability" 
        ]

def create_marketing_content(category, brand, objective, offer, medium, tone,any_specific_input, ab_testing):
    """
    Generates marketing content using OpenAI API based on the inputs provided.
    """
    openai.api_key = config.OPENAI_API_KEY  # Load the API key from the configuration file

    char_limits = {
        "email": 2000,
        "sms": 160,
        "whatsapp": 500
    }

    char_limit = char_limits.get(medium.lower(), 500)

    channel_constraints = {
        "sms": "Messages must be concise, engaging, and contextually appropriate for a mobile audience. It should not include any spam words and emojis.",
        "whatsapp": "Messages must be conversational, engaging, and resonate with a personal tone suited for WhatsApp. It can contain emojis for better visualization",
        "email": "Subject lines must be intriguing, clear, and encourage the recipient to open the email. Each subject line should be between 4 and 9 characters. It can contain emojis for better visualization but not more than 3. The email body should be concise and actionable, avoiding any spam words.",
    }

    constraints = channel_constraints.get(medium.lower(), "")

    prompt = (
    f"You are a marketing content creator with 10+ years of experience. "
    f"Create fresh and engaging marketing content based on the following inputs. "
    f"Do not refer to any previous input or outputs for content generation. \n\n"
    f"Category: {category}\n"
    f"Brand: {brand}\n"
    f"Objective: {objective}\n"
    f"Offer/Incentive: {offer}\n"
    f"Medium: {medium}\n"
    f"Tone: {tone}\n"
    f"Character Limit: {char_limit}\n"
    f"Include CTAs for better engagement.\n"
    )


    if constraints:
        prompt += f"Additional Constraints: {constraints}\n"

    if ab_testing:
        prompt += "Create two variations for A/B testing. Provide the output as a numbered list."
    else:
        prompt += "Provide 1 content messages in a numbered list format with no additional text or explanations."

    if any_specific_input:
        prompt += "And use this as specific input" + any_specific_input
    else:
        None 

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a creative marketing assistant and expert in crafting impactful messages. "
                        "Focus on adhering to the specified constraints, tailoring content to the industry context, "
                        "and ensuring the messages are engaging, actionable, and easy to read for the general public. "
                        "Do not refer to any previous input or output for content generation."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.7,
            store = False,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred while processing the request: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    content = None

    if request.method == "POST":
        category = request.form.get("category", "None")
        brand = request.form.get("brand", "None")
        objective = request.form.get("objective", "None")
        offer = request.form.get("offer", "None")
        medium = request.form.get("medium", "None")
        tone = request.form.get("tone", "None")
        specific_input = request.form.get("specific_input", "None")
        ab_testing = request.form.get("ab_testing") == "on"

        # Call the function to generate content
        content = create_marketing_content(
            category, brand, objective, offer, medium, tone,specific_input, ab_testing
        )

    return render_template("index.html", categories=CATEGORIES, mediums=MEDIUMS, tones=TONES, content=content)

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=8080, debug=True)
