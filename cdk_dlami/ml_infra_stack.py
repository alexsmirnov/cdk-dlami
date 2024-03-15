from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_secretsmanager as secrets,
    RemovalPolicy, Size,
    aws_ssm as ssm, Tags
)
from constructs import Construct

from cdk_dlami.vpc_construct import MlVPC


class MLInfraStack(Stack):
    """
    This stack creates the infrastructure for the machine learning environment.
    It creates a VPC, S3 bucket, EBS volume, and secrets for OpenAI and Huggingface.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        tags = Tags.of(self)
        tags.add("Role", "MLInfra")
        tags.add("DeploymentRegion", Stack.of(self).region)
        tags.add('AppManagerCFNStackKey', self.stack_id)
        network = MlVPC(self, "Net")
        self.vpc = network.vpc
        # S3 bucket for data
        self.bucket = s3.Bucket(self, "DataBucket",
                                versioned=True,
                                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                                removal_policy=RemovalPolicy.RETAIN
                                )
        # EBS volume for code
        self.code_volume = ec2.Volume(self, "CodeVolume",
                                      availability_zone=self.vpc.availability_zones[0],
                                      size=Size.gibibytes(125),
                                      encrypted=False,
                                      volume_type=ec2.EbsDeviceVolumeType.GP3,
                                      throughput=200,
                                      removal_policy=RemovalPolicy.RETAIN
                                      )
        # Secret for necessary credentials: OpenAI, Huggingface, Jupiter, etc.
        self.ml_secrets = secrets.Secret(self, "Secrets", secret_name="ml-secrets")
        # ssm document to run session as login shell for ec2-user.
        # This is required to run conda as it installed to ec2-user.
        ssm.CfnDocument(self, "SSMRunShellAsEc2User",
                        name="RunShellAsEc2User",
                        document_format="JSON",
                        document_type="Session",
                        target_type='/AWS::EC2::Instance',
                        content={
                            "schemaVersion": "1.0",
                            "description": "Document to hold regional settings for Session Manager",
                            "sessionType": "Standard_Stream",
                            "inputs": {
                                "s3BucketName": "",
                                "s3KeyPrefix": "",
                                "s3EncryptionEnabled": True,
                                "cloudWatchLogGroupName": "",
                                "cloudWatchEncryptionEnabled": True,
                                "cloudWatchStreamingEnabled": True,
                                "idleSessionTimeout": "50",
                                "maxSessionDuration": "",
                                "kmsKeyId": "",
                                "runAsEnabled": True,
                                "runAsDefaultUser": "ec2-user",
                                "shellProfile": {
                                    "windows": "",
                                    "linux": "exec bash --login"
                                }
                            }
                        })
