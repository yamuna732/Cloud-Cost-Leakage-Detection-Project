import boto3

ROLE_ARN = "arn:aws:iam::427684478761:role/CloudCostReadOnlyRole"


def assume_role(role_arn):
    base_session = boto3.Session(profile_name="saas")
    sts = base_session.client("sts")

    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="S3ListTest"
    )["Credentials"]

    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name="ap-south-1"
    )

    return session


def list_s3_buckets(role_arn):
    session = assume_role(role_arn)
    s3 = session.client("s3")

    buckets = s3.list_buckets()["Buckets"]

    print("\n=== S3 Buckets ===")
    for b in buckets:
        print(b["Name"])


if __name__ == "__main__":
    list_s3_buckets(ROLE_ARN)