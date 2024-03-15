#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_dlami.instance_stack import InstanceStack
from cdk_dlami.ml_infra_stack import MLInfraStack


app = cdk.App()
environment = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
infra = MLInfraStack(app, "MlInfraStack",
             env=environment,
             )
InstanceStack(app, "MLInstance",
              vpc=infra.vpc,
              bucket=infra.bucket,
              volume=infra.code_volume,
              ml_secrets=infra.ml_secrets,
              env=environment
              )
app.synth()
