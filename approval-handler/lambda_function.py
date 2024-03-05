import base64
import boto3
import json
import os
from urllib.parse import parse_qs


SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]


def lambda_handler(event, context):
    query_str = (
        base64.b64decode(event["body"]).decode("utf-8")
        if event["isBase64Encoded"]
        else event["body"]
    )

    body = parse_qs(query_str)
    payload = json.loads(body["payload"][0])
    table_name = os.environ.get("TABLE_NAME")

    if SLACK_VERIFICATION_TOKEN != payload["token"]:
        return {
            "isBase64Encoded": False,
            "statusCode": 403,
            "body": "The security token does not match SLACK_VERIFICATION_TOKEN.",
        }

    details = json.loads(payload["actions"][0]["value"])

    token = details["codePipelineToken"]
    dynamodb = boto3.client("dynamodb")
    dynamodb_response = dynamodb.update_item(
        TableName=table_name,
        Key={"action_execution_id": {"S": token}},
        UpdateExpression="SET slack_user = :input1",
        ExpressionAttributeValues={
            ":input1": {"S": payload["user"]["id"]},
        },
        ReturnValues="UPDATED_NEW",
    )

    send_approval_to_aws(details)

    msg = "Awaiting approval response."

    return {"isBase64Encoded": False, "statusCode": 200, "body": msg}


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
        token=token,
    )
