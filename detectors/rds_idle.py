import boto3
from datetime import datetime, timedelta, timezone

REGION = "ap-south-1"

DAYS = 7
CPU_THRESHOLD = 5
CONNECTION_THRESHOLD = 1
IOPS_THRESHOLD = 5

# Customer role to assume
ROLE_ARN = "arn:aws:iam::427684478761:role/CloudCostReadOnlyRole"


def assume_role(role_arn):
    """
    Use SaaS EC2 IAM role to assume customer account role.
    """
    base_session = boto3.Session()
    sts = base_session.client("sts", region_name=REGION)

    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="RDSScan"
    )["Credentials"]

    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION
    )

    return session


def get_metric(cloudwatch, db_id, metric):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=DAYS)

    data = cloudwatch.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName=metric,
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": db_id}],
        StartTime=start,
        EndTime=end,
        Period=86400,
        Statistics=["Average"],
    )

    points = data["Datapoints"]
    if not points:
        return 0

    return sum(p["Average"] for p in points) / len(points)


def find_idle_rds():
    session = assume_role(ROLE_ARN)

    rds = session.client("rds", region_name=REGION)
    cloudwatch = session.client("cloudwatch", region_name=REGION)

    idle = []

    dbs = rds.describe_db_instances()["DBInstances"]

    for db in dbs:
        db_id = db["DBInstanceIdentifier"]
        db_class = db["DBInstanceClass"]
        status = db["DBInstanceStatus"]

        if status != "available":
            continue

        cpu = get_metric(cloudwatch, db_id, "CPUUtilization")
        con = get_metric(cloudwatch, db_id, "DatabaseConnections")
        read = get_metric(cloudwatch, db_id, "ReadIOPS")
        write = get_metric(cloudwatch, db_id, "WriteIOPS")

        if (
            cpu < CPU_THRESHOLD
            and con < CONNECTION_THRESHOLD
            and read < IOPS_THRESHOLD
            and write < IOPS_THRESHOLD
        ):
            idle.append({
                "DBInstanceIdentifier": db_id,
                "DBInstanceClass": db_class
            })

    return idle


# test
if __name__ == "__main__":
    result = find_idle_rds()

    print("=== RDS Idle Check ===")
    if result:
        for db in result:
            print(f"Idle RDS: {db['DBInstanceIdentifier']} ({db['DBInstanceClass']})")
    else:
        print("No idle RDS instances found.")
