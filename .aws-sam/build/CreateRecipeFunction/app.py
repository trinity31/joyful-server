import json
import openai
import os
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

# def translate_text(text, target_language):
#     result = translate_client.translate(text, target_language)
#     return result["translatedText"]


def translate_text_with_line_breaks(text, target_language):
    creds_json = json.loads(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

    # Create credentials from the service account info
    creds = service_account.Credentials.from_service_account_info(creds_json)

    # Pass the credentials when creating the client
    translate_client = translate.Client(credentials=creds)

    # Split the text by line breaks
    lines = text.split("\n")

    # Translate each line separately
    translated_lines = [
        translate_client.translate(line, target_language=target_language)[
            "translatedText"
        ]
        for line in lines
    ]

    # Rejoin the translated lines
    translated_text = "\n".join(translated_lines)

    return translated_text


def lambda_handler(event, context):
    try:
        openai.api_key = os.environ.get("OPENAI_KEY")

        body = json.loads(event["body"])

        ingredients = body["ingredients"]
        quantity = body["quantity"]
        cuisine = body["cuisine"]
        mealtype = body["mealtype"]
        locale = body["locale"]
        special = body["special"]

        intro = "I want you to act as my personal vegan chef who can suggest delicious recipes which are nutritionally beneficial but also easy to cook at home."

        prompt = f"""
                {intro}
                Special request: {special}.
                Answer in markdown format. You should only reply
                with the recipes you recommend, and nothing else. Do not write explanations.
                The title of the recipe does not have to include cuisine type, meal type, and all the ingredients.
                The recipe must be vegan and must include the following ingredients: {ingredients}
                The recipe must indicate the amount of each ingredient for serving {quantity}. 
                Describe the detailed process to make the recipe.
                The title should be in h1 format. 
                {cuisine}.  {mealtype}
                Answer in English.
                """

        print(prompt)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            # prompt=prompt,
            messages=[
                {"role": "system", "content": "You are a vegan chef."},
                {"role": "user", "content": prompt},
            ],
        )

        result = response["choices"][0]
        # print(result)
        result_recipe = result.message.content

        import re

        match = re.search(r"^#\s(.*)$", result_recipe, re.MULTILINE)
        recipe_title = match.group(1) if match else None

        # print(result_recipe)
        # print(recipe_title)

        result_recipe_translated = (
            translate_text_with_line_breaks(result_recipe, locale)
            if locale != "en"
            else result_recipe
        )

        print(result_recipe_translated)

        # Provide the response
        response_data = {
            "result": "Success",
            "data": {"recipe": result_recipe_translated, "title": recipe_title},
        }

        print(response_data)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Or the specific origin you want to allow
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps(response_data),
        }
    except Exception as e:
        # Print the error message and traceback
        print(f"An error occurred: {str(e)}")

        # Return an error response
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"result": "Error", "message": str(e)}),
        }
