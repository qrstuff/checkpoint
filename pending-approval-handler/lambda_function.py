import os
import json
import boto3
from urllib.request import Request, urlopen
from datetime import datetime, timedelta


def lambda_handler(event, context):
    channel_id = os.environ.get("CHANNEL_ID")
    current_time = datetime.strptime(
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S"
    )

    dynamodb = boto3.client("dynamodb")
    codepipeline = boto3.client("codepipeline")
    table_name = os.environ.get("TABLE_NAME")

    db_response = dynamodb.scan(TableName=table_name)
    no_of_items = len(db_response["Items"])
    expiry = int(os.environ.get("EXPIRY_IN_HOURS"))
    x = 0

    while x < no_of_items:
        timestamp_old = datetime.strptime(
            db_response["Items"][x]["timestamp"]["S"], "%d/%m/%Y %H:%M:%S"
        )
        expires_on = timestamp_old + timedelta(hours=expiry)
        message_ts = db_response["Items"][x]["message_ts"]["S"]
        codepipeline_name = db_response["Items"][x]["pipeline_name"]["S"]
        stage_name = db_response["Items"][x]["pipeline_stage"]["S"]
        action_name = db_response["Items"][x]["pipeline_action"]["S"]
        token = db_response["Items"][x]["pipeline_token"]["S"]

        data = {
            "attachments": [],
            "channel": channel_id,
            "text": "*{}* action for *{}* expired in {} hours due to no response.".format(
                action_name, codepipeline_name, expiry
            ),
            "ts": message_ts,
        }
        headers = {
            "Authorization": "Bearer " + str(os.environ.get("SLACK_OAUTH_TOKEN")),
            "Content-type": "application/json; charset=utf-8",
        }

        if current_time > expires_on:
            response = codepipeline.put_approval_result(
                pipelineName=codepipeline_name,
                stageName=stage_name,
                actionName=action_name,
                result={"summary": "", "status": "Rejected"},
                token=token,
            )

            req = Request(
                "https://slack.com/api/chat.update",
                headers=headers,
                data=json.dumps(data).encode("utf-8"),
                method="POST",
            )

            response = json.loads(urlopen(req).read().decode("utf-8"))

            dynamodb_response = dynamodb.delete_item(
                Key={
                    "pipeline_name": {
                        "S": codepipeline_name,
                    }
                },
                TableName=table_name,
            )

        x += 1
