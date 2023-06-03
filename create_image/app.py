import json
import openai
import os


def lambda_handler(event, context):
    openai.api_key = os.environ.get("OPENAI_KEY")

    body = json.loads(event["body"])

    title = body["title"]

    # print(title)

    response = openai.Image.create(prompt=title, n=1, size="1024x1024")

    result_image = response["data"][0]["url"]

    # print(result_image)

    response_data = {
        "result": "Success",
        "data": {"image": result_image},
    }

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Or the specific origin you want to allow
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps(response_data),
    }
