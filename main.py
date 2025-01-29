from flask import Flask, render_template, request, redirect, url_for
import openai 
import os

API_KEY = os.environ.get("API_KEY")


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
    "Automotive & Accessories",
]

MEDIUMS = ["None", "SMS", "WhatsApp", "Email"]

TONES = [
    "None",
    "Anticipation",
    "Joy",
    "Trust",
    "Fear of Missing Out(FOMO)",
    "Surprise",
    "Excitement",
    "Curiosity",
    "Calmness",
    "Security",
    "Kindness",
    "Admiration",
    "Thankfulness",
    "Hope",
    "Reliability",
]


def create_marketing_content(category, brand, objective, offer, medium, tone, specific_input, ab_testing):
    openai.api_key = config.API_KEY

    char_limits = {
        "email": 2000,
        "sms": 160,
        "whatsapp": 500
    }

    char_limit = char_limits.get(medium.lower(), 500)

    channel_constraints = {
        "sms": "Messages must be concise, engaging, and contextually appropriate for a mobile audience. It should not include any spam words and emojis.",
        "whatsapp": "Messages must be conversational, engaging, and resonate with a personal tone suited for WhatsApp. It can contain emojis for better visualization.",
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

    if specific_input:
        prompt += f"And use this as specific input: {specific_input}"

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
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred while processing the request: {e}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Collect form data
        form_data = {
            "category": request.form.get("category", "None"),
            "brand": request.form.get("brand", "None"),
            "objective": request.form.get("objective", "None"),
            "offer": request.form.get("offer", "None"),
            "medium": request.form.get("medium", "None"),
            "tone": request.form.get("tone", "None"),
            "specific_input": request.form.get("specific_input", "None"),
            "ab_testing": request.form.get("ab_testing") == "on",
        }

        # Generate content
        content = create_marketing_content(
            form_data["category"],
            form_data["brand"],
            form_data["objective"],
            form_data["offer"],
            form_data["medium"],
            form_data["tone"],
            form_data["specific_input"],
            form_data["ab_testing"],
        )

        # Store results and redirect to the result page
        return redirect(
            url_for(
                "result",
                content=content,
                **form_data,
            )
        )

    return render_template("index.html", categories=CATEGORIES, mediums=MEDIUMS, tones=TONES)


@app.route("/result")
def result():
    content = request.args.get("content", "")
    form_data = {key: request.args.get(key, "") for key in request.args if key != "content"}
    return render_template("result.html", content=content, form_data=form_data)


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(debug=True)

