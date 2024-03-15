import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
    Tags, CfnOutput,
)
from aws_cdk.aws_s3_assets import Asset
from constructs import Construct

dirname = os.path.dirname(__file__)

pytorch_gpu_ami = 'Deep Learning Proprietary Nvidia Driver AMI GPU PyTorch 2.0.1 (Amazon Linux 2) ????????'
neuron_ubuntu_ami = "Deep Learning AMI Neuron (Ubuntu 22.04) ????????"
nvidia_amazon_ami = "Deep Learning Proprietary Nvidia Driver AMI (Amazon Linux 2) Version ??.?"


class InstanceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc, bucket, volume, ml_secrets, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        tags = Tags.of(self)
        tags.add("Role", "MLInstance")
        tags.add("DeploymentRegion", Stack.of(self).region)
        tags.add('AppManagerCFNStackKey', self.stack_id);
        # AMI
        dl_ami = ec2.MachineImage.lookup(name=nvidia_amazon_ami, owners=["amazon"],
                                         filters={"state": ["available"]}
                                         )
        # create instance from DLAMI.
        instance_type = ec2.InstanceType("g5.xlarge")
        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "SSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        instance = ec2.Instance(self, "Instance",
                                instance_name="Notebook",
                                instance_type=instance_type,
                                machine_image=dl_ami,
                                vpc=vpc,
                                availability_zone=vpc.availability_zones[0],
                                vpc_subnets=ec2.SubnetSelection(
                                    subnet_type=ec2.SubnetType.PUBLIC
                                ),
                                allow_all_outbound=True,
                                associate_public_ip_address=True,
                                ssm_session_permissions=True,
                                role=role,
                                # block_devices=[
                                #     ec2.BlockDevice(device_name="/dev/xvda", volume=ec2.BlockDeviceVolume.ebs(10, encrypted=False))
                                # ],
                                )
        volume.grant_attach_volume_by_resource_tag(role, [instance])
        bucket.grant_read_write(role)
        ml_secrets.grant_read(role)
        # Script in S3 as Asset
        asset = Asset(self, "Asset", path=os.path.join(dirname, "..", "scripts", "configure.sh"))
        # Attach volume to instance
        target_device = "/dev/xvdf"
        instance.user_data.add_commands(
            "InstanceID=$(/opt/aws/bin/ec2-metadata -i | cut -d ' ' -f 2)",
            f'aws --region {Stack.of(self).region} ec2 attach-volume --volume-id {volume.volume_id} --instance-id "$InstanceID" --device {target_device}',
            # Wait until the volume has attached
            f"while ! test -e {target_device}; do sleep 1; done"
        )
        local_path = instance.user_data.add_s3_download_command(
            bucket=asset.bucket,
            bucket_key=asset.s3_object_key
        )
        # Userdata executes script from S3
        instance.user_data.add_execute_file_command(
            file_path=local_path,
            arguments=bucket.bucket_name
        )
        asset.grant_read(role)
        Tags.of(self).add("Role", "Jupiter")
        Tags.of(instance).add("Name", "Notebook")
        CfnOutput(self, "InstanceId", value=instance.instance_id)
