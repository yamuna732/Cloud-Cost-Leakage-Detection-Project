import boto3

# 👇 paste your CUSTOMER role ARN here
ROLE_ARN = "arn:aws:iam::427684478761:role/CloudCostReadOnlyRole"

# use SaaS AWS profile
base_session = boto3.Session(profile_name="saas")

sts = base_session.client("sts")

# assume customer role
creds = sts.assume_role(
    RoleArn=ROLE_ARN,
    RoleSessionName="test"
)["Credentials"]

# create session for customer account
session = boto3.Session(
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
    region_name="ap-south-1"
)

# test access: list EC2
ec2 = session.client("ec2")

response = ec2.describe_instances()

print("✅ SUCCESS — Connected to CUSTOMER account")
print("EC2 reservations:", len(response["Reservations"]))