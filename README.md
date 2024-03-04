# checkpoint

CloudFormation template for creating the AWS components for [Slack](https://slack.com/) notification for [CodePipeline Manual Approval Actions](https://docs.aws.amazon.com/codepipeline/latest/userguide/approvals.html).

It also contains a lambda handler function to update the slack message according to the received approval/denial event from slack, console or codepipeline timeout source.

## Usage

#### Prerequisites:

1. [Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) AWS CLI.

2. Create [Slack app](https://api.slack.com/start/quickstart#creating).

3. Add the following [scopes](https://api.slack.com/start/quickstart#scopes) for bot token OAuth.
```
channels:read
chat:write
chat:write.customize
```

4. [Install and authorize](https://api.slack.com/start/quickstart#installing) the app for the workspace.

5. Add a [manual approval](https://docs.aws.amazon.com/codepipeline/latest/userguide/approvals-action-add.html) action in the Codepipeline. Set a timeout in the manual approval step.

6. Create S3 bucket to store the packaged code used in deployment of Lambda functions.

#### Template Deployment:

The cloudformation template can be deployed directly using cli. Two steps are required: packaging the template to upload the lambda function code and creating the stack.

```shell
aws cloudformation package --template-file ./template.yml --s3-bucket checkpointest --output-template-file out.yml

aws cloudformation create-stack --stack-name checkpointest --template-body file://out.yml \
--parameters \
ParameterKey=ProjectName,ParameterValue=checkpointest \
ParameterKey=SlackVerificationToken,ParameterValue=9bJVwa3JyQ1sEtoNNIlT96m8 \
ParameterKey=SlackOAuthToken,ParameterValue=xoxb-456293491349-6450191577376-fi3qcHVRXkSUuiKmPsHABnqM \
ParameterKey=ChannelId,ParameterValue=C03PULHKCLS \
--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
```
After completion of stack deployment, edit the Manual Approval Step in pipeline. In the field **SNS topic ARN -** ***optional***, select the SNS topic Approval-Notification, save the pipeline and **Release Changes**.

#### Available Parameters

Following parameters are available for customization. Defaults can be set in the template, and can be overridden via cli as mentioned in the [Template Deployment](#Template-Deployment).

```yaml
  ApprovalStepArn:
    Type: CommaDelimitedList
    Description: Arn for the manual approval for IAM policy, e.g., format (arn:aws:codepipeline:region:aws-account-id:pipeline-name/stage-name/action-name).
  ChannelId:
    Type: String
    Description: Channel ID of the Slack channel.
  ProjectName:
    Type: String
    Description: Project name or app name.
  SlackOAuthToken:
    Type: String
    Description: OAuth token for API request to Slack.
  SlackVerificationToken:
    Type: String
    Description: Verification Token for Approval Handler Function
  SnsTopicName:
    Type: String
    Description: SNS topic name.
  TableName:
    Type: String
    Description: Table name to be created in DynamoDB.
```


## License

See the [LICENSE](LICENSE) file.

## Notes

From the team at [QRStuff](https://qrstuff.com/) with ❤️ for automation with [Cloudformation](https://aws.amazon.com/cloudformation/).
