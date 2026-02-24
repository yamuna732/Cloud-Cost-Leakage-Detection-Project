import boto3
from datetime import datetime, timezone, timedelta

DAYS_THRESHOLD = 60
ROLE_ARN = "arn:aws:iam::427684478761:role/CloudCostReadOnlyRole"
REGION = "ap-south-1"


def assume_role(role_arn):
    # SaaS EC2 IAM role provides base credentials automatically
    base_session = boto3.Session()
    sts = base_session.client("sts", region_name=REGION)

    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="S3Scan"
    )["Credentials"]

    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION
    )

    return session


def get_latest_object_date(s3_client, bucket_name):
    paginator = s3_client.get_paginator("list_objects_v2")
    latest_date = None

    for page in paginator.paginate(Bucket=bucket_name):
        if "Contents" not in page:
            continue

        for obj in page["Contents"]:
            obj_date = obj["LastModified"]
            if not latest_date or obj_date > latest_date:
                latest_date = obj_date

    return latest_date


def find_unused_s3():
    session = assume_role(ROLE_ARN)
    s3 = session.client("s3", region_name=REGION)

    unused = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_THRESHOLD)

    buckets = s3.list_buckets()["Buckets"]

    for bucket in buckets:
        name = bucket["Name"]
        latest = get_latest_object_date(s3, name)

        # empty bucket
        if latest is None:
            unused.append({
                "Name": name,
                "SizeGB": 0
            })
            continue

        # inactive bucket
        if latest < cutoff:
            unused.append({
                "Name": name,
                "SizeGB": 0
            })

    return unused


# test runner
if __name__ == "__main__":
    results = find_unused_s3()

    print("\n=== Forgotten S3 Buckets ===")

    if not results:
        print("No forgotten buckets found")
    else:
        for r in results:
            print(r)
