
# This function is triggered via API Gateway when a user acts on the Slack interactive message sent by approval_requester.py.
from urllib.parse import parse_qs
import json
import os
import boto3
import base64

SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']

#Triggered by API Gateway
#It kicks off a particular CodePipeline project
def lambda_handler(event, context):
	# print("Received event: " + json.dumps(event, indent=2))
	body = parse_qs(base64.b64decode(event['body']).decode('utf-8'))
	payload = json.loads(body['payload'][0])

	# Validate Slack token
	if SLACK_VERIFICATION_TOKEN == payload['token']:
		details = json.loads(payload['actions'][0]['value'])
		send_slack_message(details)
		action_name = details["actionName"]

		# This will replace the interactive message with a simple text response.
		# You can implement a more complex message update if you would like.
		return  {
			"isBase64Encoded": "false",
			"statusCode": 200,
			"body": action_name + " for <" + details['consoleLink'] + "|" + details['codePipelineName'] + "> was :white_check_mark: approved by <@" + payload['user']['id'] + ">."
				if details["approve"]
				else action_name + " for <" + details['consoleLink'] + "|" + details['codePipelineName'] + "> was :x: denied by <@" + payload['user']['id'] + ">."
		}
	else:
		return  {
			"isBase64Encoded": "false",
			"statusCode": 403,
			"body": "Failed to verify incoming request from Slack."
		}

def send_slack_message(action_details):
	codepipeline_status = "Approved" if action_details["approve"] else "Rejected"
	codepipeline_name = action_details["codePipelineName"]
	token = action_details["codePipelineToken"]
	action_name = action_details["actionName"]
	stage_name = action_details["stageName"]
	client = boto3.client('codepipeline')

	response_approval = client.put_approval_result(
							pipelineName=codepipeline_name,
							stageName=stage_name,
							actionName=action_name,
							result={'summary':'','status':codepipeline_status},
							token=token)

	print(response_approval)
