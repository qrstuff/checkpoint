import os
import json
from urllib.request import Request, urlopen


SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

def lambda_handler(event, context):
    # for debugging only
    # print("received event:", json.dumps(event, indent=2))

    message = event["Records"][0]["Sns"]["Message"]
    data = json.loads(message)

    console_link = data["consoleLink"]
    token = data["approval"]["token"]
    codepipeline_name = data["approval"]["pipelineName"]
    action_name = data["approval"]["actionName"]
    stage_name = data["approval"]["stageName"]

    slack_message = {
        "text": "*{}* action for <{}|{}> is awaiting approval.".format(action_name, console_link, codepipeline_name),
        "attachments": [
            {
                "text": "Confirm whether to continue or not.",
                "fallback": "You are unable to approve/reject a pipeline action.",
                "callback_id": "checkpoint_approval",
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
                            "text": "This will continue the execution of " + codepipeline_name + " pipeline.",
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

    req = Request(SLACK_WEBHOOK_URL, json.dumps(slack_message).encode("utf-8"))
    response = urlopen(req)
    response.read()
    return None
