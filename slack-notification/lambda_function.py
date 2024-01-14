import os
import json
import boto3
from urllib.request import Request, urlopen
from datetime import datetime



def lambda_handler(event, context):
    # for debugging only
    # print("received event:", json.dumps(event, indent=2))

    channel_id = os.environ.get("CHANNEL_ID")
    message = event["Records"][0]["Sns"]["Message"]
    data = json.loads(message)
    dynamodb = boto3.client('dynamodb')

    console_link = data["consoleLink"]
    token = data["approval"]["token"]
    codepipeline_name = data["approval"]["pipelineName"]
    action_name = data["approval"]["actionName"]
    stage_name = data["approval"]["stageName"]
    message_id = event['Records'][0]['Sns']['MessageId']

    data = {
        "channel": channel_id,
        "icon_emoji": ":pencil:",
        "text": "*{}* action for <{}|{}> is awaiting approval.".format(
            action_name, console_link, codepipeline_name
        ),
        "username": codepipeline_name,
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
                        "value": json.dumps(
                            {
                                "actionName": action_name,
                                "approve": True,
                                "consoleLink": console_link,
                                "codePipelineToken": token,
                                "codePipelineName": codepipeline_name,
                                "stageName": stage_name,
                            }
                        ),
                        "confirm": {
                            "title": "Do you really want to do this?",
                            "text": "This will continue the execution of {} pipeline.".format(codepipeline_name),
                            "ok_text": "Confirm",
                            "dismiss_text": "Cancel",
                        },
                    },
                    {
                        "name": "deployment",
                        "text": "Cancel",
                        "type": "button",
                        "value": json.dumps(
                            {
                                "actionName": action_name,
                                "approve": False,
                                "consoleLink": console_link,
                                "codePipelineToken": token,
                                "codePipelineName": codepipeline_name,
                                "stageName": stage_name,
                            }
                        ),
                    },
                ],
            }
        ],
    }

    headers = {
        'Authorization': 'Bearer '+str(os.environ.get("SLACK_OAUTH_TOKEN")),
        'Content-type': 'application/json; charset=utf-8',
    }

    req = Request('https://slack.com/api/chat.postMessage', headers=headers, data=json.dumps(data).encode("utf-8"), method='POST')

    response = json.loads(urlopen(req).read().decode('utf-8'))
    message_ts = response["message"]["ts"]

    current_timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    dynamodb.put_item(
        TableName='ManualApprovalTracker01',
        Item={
            'message_id': {
                'S' : message_id
            },
            'message_ts': {
                'S': message_ts
            },
            'timestamp': {
                'S' : current_timestamp
            },
            'pipeline_name': {
                'S' : codepipeline_name
            },
            'pipeline_stage': {
                'S' : stage_name
            },
            'pipeline_action': {
                'S' : action_name
            },
            'pipeline_token': {
                'S' : token
            }
        }
    )

