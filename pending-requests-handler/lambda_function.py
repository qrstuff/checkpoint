import os
import json
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    channel_id = os.environ.get("CHANNEL_ID")
    current_time = datetime.strptime(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S")

    dynamodb = boto3.client('dynamodb')
    codepipeline = boto3.client('codepipeline')

    db_response = dynamodb.scan(
        TableName='ManualApprovalTracker01'
    )
    no_of_items = len(db_response['Items'])

    expiry = os.environ.get("EXPIRY_IN_HOURS")
    data = {
        "channel": channel_id,
        "icon_emoji": ":heavy_multiplication_x:",
        "text": "*{}* action approval for *{}* expired in {} hours due to no response.".format(
            action_name, codepipeline_name, expiry
        )
    }

    x = 0

    while x < no_of_items:

        codepipeline_name = db_response['Items'][x]['pipeline_name']['S']
        stage_name = db_response['Items'][x]['pipeline_stage']['S']
        action_name = db_response['Items'][x]['pipeline_action']['S']
        token = db_response['Items'][x]['pipeline_token']['S']
        timestamp_old = datetime.strptime(db_response['Items'][x]['timestamp']['S'],'%d/%m/%Y %H:%M:%S')
        expires_on =  timestamp_old + timedelta(hours=expiry)

        if current_time > expires_on:
            response=codepipeline.put_approval_result(
                pipelineName=codepipeline_name,
                stageName=stage_name,
                actionName=action_name,
                result={"summary": "", "status": "Rejected"},
                token=token,
            )

        x+=1