"""Generating CloudFormation template."""
from ipaddress import ip_network

from ipify import get_ip

from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template,
)
ApplicationName="myhelloworld"
ApplicationPort = "3000"

GithubAccount="edwin58385"
GithubAnsibleURL="https://github.com/{}/ans".format(GithubAccount)

AnsiblePullCmd="/usr/bin/ansible-pull -U {} {}.yml -i \
localhost".format(GithubAnsibleURL,ApplicationName)

PublicCidrIp = str(ip_network(get_ip()))

t = Template()
t.set_description("Effective DevOps in AWS: HelloWorld web application")
#t.add_description("Effective DevOps in AWS: HelloWorld web application")

t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

t.add_resource(ec2.SecurityGroup(
    "SecurityGroup",
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp=PublicCidrIp,
            #CidrIp="0.0.0.0/0",
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort=ApplicationPort,
            ToPort=ApplicationPort,
            CidrIp="0.0.0.0/0",
        ),
    ],
))
'''
ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo yum install --enablerepo=epel -y nodejs",
    "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
    "wget http://bit.ly/2vVvT18 -O /etc/init/helloworld.conf",
    "start helloworld"
]))

ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo apt-get update",
    "sudo apt-get install -y nodejs",
    "wget http://bit.ly/2vESNuc -O /home/ubuntu/myhelloworld.js",
    "wget 'https://docs.google.com/uc?export=download&id=1CYoHy14TMtiHvfyGIzzjaIeKSPLkJ275' -O /lib/systemd/system/myhelloworld.service",
    # download myhelloworld.service.txt as /lib/systemd/system/myhelloworld.service
    "sudo service myhelloworld start"
    #"wget http://bit.ly/2vESNuc -O /home/ubuntu/myhelloworld.js",
    #"wget http://bit.ly/2vVvT18 -O /etc/init/myhelloworld.conf",
    #"nodejs helloworld.js"
    #"start helloworld"
]))
'''
ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo apt-get update",
    "sudo apt-get install -y git",
    "sudo apt-get install -y ansible",
    AnsiblePullCmd,
    "echo '*/1 * * * * ubuntu {}' > /home/ubuntu/ansiblepull".format(AnsiblePullCmd),
    "sudo cp /home/ubuntu/ansiblepull /etc/cron.d/ansiblepull"
]))

t.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-0d53808c8c345ed07",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
))

t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("", [
        "http://", GetAtt("instance", "PublicDnsName"),
        ":", ApplicationPort
    ]),
))

print(t.to_json())