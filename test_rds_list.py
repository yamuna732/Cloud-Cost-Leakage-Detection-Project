# test_rds_list.py
import boto3

rds = boto3.client("rds")
dbs = rds.describe_db_instances()["DBInstances"]

print("RDS count:", len(dbs))

for db in dbs:
    print(db["DBInstanceIdentifier"], db["DBInstanceStatus"])