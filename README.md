# checkpoint

CloudFormation template for creating the AWS components for [Slack](https://slack.com/) notification for [CodePipeline Manual Approval Actions](https://docs.aws.amazon.com/codepipeline/latest/userguide/approvals.html).

The template also includes a Lambda function that runs on schedule to reject any pending approvals beyond a specified expiry value.

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

5. Add a [manual approval](https://docs.aws.amazon.com/codepipeline/latest/userguide/approvals-action-add.html) action in the Codepipeline.

6. Create S3 bucket to store the packaged code used in deployment of Lambda functions.

#### Template Deployment:

The cloudformation template can be deployed directly using cli. Two steps are required: packaging the template to upload the lambda function code and creating the stack.

```shell
aws cloudformation package --template-file ./template.yml --s3-bucket s3-bucket-name --output-template-file out.yml

aws cloudformation create-stack --stack-name checkpoint --template-body file://out.yml \
--parameters \
ParameterKey=ProjectName,ParameterValue=project-name \
ParameterKey=SlackVerificationToken,ParameterValue=slack-verfication-token \
ParameterKey=SlackOAuthToken,ParameterValue=slack-oauth-token \
ParameterKey=ChannelId,ParameterValue=slack-channel-id \
--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
```

#### Available Parameters

Following parameters are available for customization. Defaults can be set in the template, and can be overridden via cli as mentioned in the [Template Deployment](#Template-Deployment).

```yaml
  ApprovalStepArn:
    Type: CommaDelimitedList
    Description: Arn for the manual approval, e.g., format (arn:aws:codepipeline:region:aws-account-id:pipeline-name/stage-name/action-name).
  ChannelId:
    Type: String
    Description: Channel ID of the Slack channel.
  CronExpression:
    Type: String
    Description: Cron expression for running the pending approval rejection function.
  ExpiryInHours:
    Type: Number
    Description: Expiry of the approval check in no. of hours.
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
