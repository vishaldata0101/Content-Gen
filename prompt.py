import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# Access environment variables: API_KEY
API_KEY = os.environ.get("API_KEY")


# Define function to generate marketing content through OpenAI's GPT-4

def create_marketing_content(category, brand, objective, medium, cta_button=None, offer=None, tone=None, specific_input=None, ab_testing=False):
    openai.api_key = API_KEY

    # Character limits per medium
    char_limits = {
        "email": 1000,
        "sms": 160,
        "whatsapp": 500
    }
    char_limit = char_limits.get(medium.lower(), 500)
    
    # Double the limit for A/B testing
    if ab_testing:
        char_limit *= 2

    # Medium-specific constraints
    channel_constraints = {
        "sms": "Messages must be concise, engaging, and contextually appropriate for a mobile audience. Avoid spam words and emojis.",
        "whatsapp": "Messages should be conversational, engaging, and resonate with a personal tone suited for WhatsApp. Emojis can be included for better visualization.",
        "email": "Subject lines must be intriguing, clear, and encourage the recipient to open the email (4-9 words). Use at most 3 emojis. Email body should be concise, actionable, and avoid spam words."
    }
    constraints = channel_constraints.get(medium.lower(), "")

    # Constructing the prompt
    prompt_parts = [
        "You are a marketing content creator with 10+ years of experience.",
        "Create fresh and engaging marketing content based on the following inputs.",
        "Do not refer to any previous input or outputs for content generation.",
        f"Category: {category}",
        f"Brand: {brand}",
        f"Objective: {objective}",
        f"Medium: {medium}",
        f"Character Limit: {char_limit}"
    ]

    if offer:
        prompt_parts.append(f"Offer/Incentive: {offer}")
    if tone:
        prompt_parts.append(f"Tone: {tone}")
    if constraints:
        prompt_parts.append(f"Constraints: {constraints}")
    if cta_button:
        prompt_parts.append(f"Include CTA button at the end of the message: {cta_button}")
    if specific_input:
        prompt_parts.append(f"Use this as specific input: {specific_input}")

    # A/B Testing variations
    if ab_testing:
        prompt_parts.append("Create two variations for A/B testing. Provide the output as a numbered list.")
    else:
        prompt_parts.append("Provide a content message with no additional text or explanations with proper formatting and alignment and indentaion based on the selected medium.") 

    prompt = "\n".join(prompt_parts)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative marketing assistant. Craft impactful, engaging, and industry-specific content that is easy to read and actionable."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=char_limit,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Error: {e}"
    


# Define function to improve existing marketing content based on specific comments
def improve_marketing_content(existing_content, category, brand, medium, specific_input, ab_testing=False):
    openai.api_key = API_KEY

    char_limits = {
        "email": 1000,
        "sms": 160,
        "whatsapp": 500
    }

    char_limit = char_limits.get(medium.lower(), 500)

    # Double the limit for A/B testing
    if ab_testing:
        char_limit *= 2

    prompt = (
            f"Modify the existing content based on the specific comments provided. "
            f"Ensure the new content reflects the provided category, brand, and medium, and is more engaging, relevant, and aligned with the feedback. "
            f"Focus on enhancing the message while keeping the core meaning intact. "
            f"Stay within the provided token limit and ensure the content remains concise, clear, and impactful.\n\n"
            f"Existing Content: {existing_content}\n"
            f"Category: {category}\n"
            f"Brand: {brand}\n"
            f"Medium: {medium}\n"
            f"Specific Comments to modify the content: {specific_input}\n\n"
            f"Character Limit: {char_limit}\n"
            f"Please revise the existing content based on the specific comments while reflecting the context of the category, brand, and medium."
    )
    # A/B Testing variations
    if ab_testing:
        prompt += "Create two variations for A/B testing. Provide the output as a numbered list."
    else:
        prompt += "Provide a content message with no additional text or explanations with proper formatting and alignment and indentaion based on the selected medium."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative marketing assistant. Craft impactful, engaging, and industry-specific content that is easy to read and actionable."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=char_limit,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Error: {e}"



