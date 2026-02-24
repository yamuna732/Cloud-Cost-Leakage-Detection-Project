import boto3

ec2 = boto3.client("ec2")

reservations = ec2.describe_instances()["Reservations"]

instances = []
for r in reservations:
    for inst in r["Instances"]:
        instances.append(
            (
                inst["InstanceId"],
                inst["State"]["Name"]
            )
        )

print("EC2 count:", len(instances))

for i in instances:
    print(i[0], i[1])