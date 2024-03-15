from aws_cdk import (
    # Duration,
    aws_ec2 as ec2,
    # aws_sqs as sqs,
)
from constructs import Construct


class MlVPC(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.vpc = ec2.Vpc(self, "VPC",
                           subnet_configuration=[
                               ec2.SubnetConfiguration(
                                   name="public",
                                   subnet_type=ec2.SubnetType.PUBLIC,
                                   reserved=False,
                                   # IPv4 specific properties
                                   map_public_ip_on_launch=False,
                                   cidr_mask=24
                               )
                           ],
                           max_azs=2,
                           nat_gateways=0
                           )