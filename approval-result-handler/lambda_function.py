import base64, os, boto3, json
from urllib.parse import parse_qs
from urllib.request import Request, urlopen


def lambda_handler(event, context):
    channel_id = os.environ.get("CHANNEL_ID")
    table_name = os.environ.get("TABLE_NAME")

    action_details = event["detail"]
    codepipeline_name = action_details["pipeline"]
    action_execution_id = action_details["action-execution-id"]
    action_name = action_details["action"]
    execution_summary = action_details["execution-result"].get(
        "external-execution-summary"
    )

    dynamodb = boto3.client("dynamodb")
    response = dynamodb.get_item(
        TableName=table_name, Key={"action_execution_id": {"S": action_execution_id}}
    )
    console_link = response["Item"]["console_link"]["S"]
    slack_user = response["Item"]["slack_user"]["S"]
    message_ts = response["Item"]["message_ts"]["S"]

    if slack_user:
        user = "@"+slack_user
    elif execution_summary:
        region = os.environ.get('AWS_REGION')
        username = execution_summary.split("user/", 1)[1]
        template = "https://us-east-1.console.aws.amazon.com/iam/home?region={0}#/users/details/{1}|{1}"
        user = template.format(region, username)
    else:
        user = None

    if action_details["state"] == "SUCCEEDED":
        msg_template = (
            "*{}* action for <{}|{}> was :white_check_mark: approved by <{}>."
        )
        msg = msg_template.format(action_name, console_link, codepipeline_name, user)
    else:
        error_code = action_details["execution-result"]["error-code"]
        if error_code == "TimeoutError":
            msg_template = "*{}* action for <{}|{}> expired due to no response."
            msg = msg_template.format(action_name, console_link, codepipeline_name)

        else:
            msg_template = "*{}* action for <{}|{}> was :x: denied by <{}>"
            msg = msg_template.format(
                action_name, console_link, codepipeline_name, user
            )

    data = {
        "attachments": [],
        "channel": channel_id,
        "text": msg,
        "ts": message_ts,
    }
    headers = {
        "Authorization": "Bearer " + str(os.environ.get("SLACK_OAUTH_TOKEN")),
        "Content-type": "application/json; charset=utf-8",
    }

    req = Request(
        "https://slack.com/api/chat.update",
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
        method="POST",
    )

    response = json.loads(urlopen(req).read().decode("utf-8"))

    dynamodb_response = dynamodb.delete_item(
        Key={
            "action_execution_id": {
                "S": action_execution_id,
            }
        },
        TableName=table_name,
    )
