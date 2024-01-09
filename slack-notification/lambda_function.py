
# This function is invoked via SNS when the CodePipeline manual approval action starts.
# It will take the details from this approval notification and sent an interactive message to Slack that allows users to approve or cancel the deployment.
import os
import json
import logging
import urllib.parse
from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# This is passed as a plain-text environment variable for ease of demonstration.
# Consider encrypting the value with KMS or use an encrypted parameter in Parameter Store for production deployments.

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    message = event["Records"][0]["Sns"]["Message"]
    data = json.loads(message)
    console_link = data["consoleLink"]
    token = data["approval"]["token"]
    codepipeline_name = data["approval"]["pipelineName"]
    action_name = data["approval"]["actionName"]
    stage_name = data["approval"]["stageName"]

    slack_message = {
        "text":  action_name + " for <" + console_link + "|" + codepipeline_name + "> is awaiting approval.",
        "attachments": [
            {
                "text": "Confirm whether to deploy or not.",
                "fallback": "You are unable to promote a production deployment.",
                "callback_id": "wopr_game",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "deployment",
                        "text": "Confirm",
                        "style": "danger",
                        "type": "button",
                        "value": json.dumps({"actionName": action_name, "approve": True, "consoleLink": console_link, "codePipelineToken": token, "codePipelineName": codepipeline_name, "stageName": stage_name}),
                        "confirm": {
                            "title": "Do you really want to do this?",
                            "text": "This will trigger deployment of " + codepipeline_name + " to production environment.",
                            "ok_text": "Confirm",
                            "dismiss_text": "Cancel"
                        }
                    },
                    {
                        "name": "deployment",
                        "text": "Cancel",
                        "type": "button",
                        "value": json.dumps({"actionName": action_name, "approve": False, "consoleLink": console_link, "codePipelineToken": token, "codePipelineName": codepipeline_name, "stageName": stage_name})
                    }
                ]
            }
        ]
    }

    req = Request(SLACK_WEBHOOK_URL, json.dumps(slack_message).encode('utf-8'))
    response = urlopen(req)
    response.read()
    return None
