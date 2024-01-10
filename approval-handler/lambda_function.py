import base64
import boto3
import json
import os
from urllib.parse import parse_qs


SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

def lambda_handler(event, context):
    # for debugging only
    # print("received event:", json.dumps(event, indent=2))

    query_str = base64.b64decode(event["body"]).decode("utf-8") if event["isBase64Encoded"] else event["body"]

    body = parse_qs(query_str)
    payload = json.loads(body["payload"][0])

    if SLACK_VERIFICATION_TOKEN != payload["token"]:
        return {
            "isBase64Encoded": "false",
            "statusCode": 403,
            "body": "The security token does not match SLACK_VERIFICATION_TOKEN."
        }

    details = json.loads(payload["actions"][0]["value"])
    send_approval_to_aws(details)

    msg = "*{}* action for <{}|{}> was :white_check_mark: approved by <@{}>." if details["approve"] else "*{}* action for <{}|{}> was :x: denied by <@{}>"

    return  {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": msg.format(details["actionName"], details["consoleLink"], details["codePipelineName"], payload["user"]["id"]),
    }

def send_approval_to_aws(action_details):
    codepipeline_status = "Approved" if action_details["approve"] else "Rejected"
    codepipeline_name = action_details["codePipelineName"]
    token = action_details["codePipelineToken"]
    action_name = action_details["actionName"]
    stage_name = action_details["stageName"]
    client = boto3.client("codepipeline")

    response_approval = client.put_approval_result(
										pipelineName=codepipeline_name,
										stageName=stage_name,
										actionName=action_name,
										result={"summary": "", "status": codepipeline_status},
										token=token)

    # for debugging only
    # print("approval response:", response_approval)
