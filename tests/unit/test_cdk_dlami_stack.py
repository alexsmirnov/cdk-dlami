import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_dlami.ml_infra_stack import MLInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_dlami/ml_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MLInfraStack(app, "cdk-dlami")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
