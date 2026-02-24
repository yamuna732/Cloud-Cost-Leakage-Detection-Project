import boto3
from datetime import datetime, timedelta, timezone

CPU_THRESHOLD = 5
NETWORK_THRESHOLD = 1000000
STOPPED_DAYS = 7
REGION = "ap-south-1"


def find_idle_ec2():
    ec2 = boto3.client("ec2", region_name=REGION)
    cw = boto3.client("cloudwatch", region_name=REGION)

    idle_instances = []

    paginator = ec2.get_paginator("describe_instances")

    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                state = instance["State"]["Name"]

                # Rule 1 — stopped long time
                if state == "stopped":
                    launch_time = instance["LaunchTime"]
                    now = datetime.now(timezone.utc)
                    stopped_days = (now - launch_time).days

                    if stopped_days >= STOPPED_DAYS:
                        idle_instances.append({
                            "InstanceId": instance_id,
                            "InstanceType": instance_type
                        })
                    continue

                # Metrics window
                end = datetime.now(timezone.utc)
                start = end - timedelta(days=7)

                cpu = cw.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName="CPUUtilization",
                    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    StartTime=start,
                    EndTime=end,
                    Period=86400,
                    Statistics=["Average"]
                )

                if not cpu["Datapoints"]:
                    continue

                avg_cpu = sum(dp["Average"] for dp in cpu["Datapoints"]) / len(cpu["Datapoints"])

                net_in = cw.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName="NetworkIn",
                    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    StartTime=start,
                    EndTime=end,
                    Period=86400,
                    Statistics=["Sum"]
                )

                net_out = cw.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName="NetworkOut",
                    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    StartTime=start,
                    EndTime=end,
                    Period=86400,
                    Statistics=["Sum"]
                )

                total_in = sum(dp["Sum"] for dp in net_in["Datapoints"]) if net_in["Datapoints"] else 0
                total_out = sum(dp["Sum"] for dp in net_out["Datapoints"]) if net_out["Datapoints"] else 0

                if avg_cpu < CPU_THRESHOLD and (total_in + total_out) < NETWORK_THRESHOLD:
                    idle_instances.append({
                        "InstanceId": instance_id,
                        "InstanceType": instance_type
                    })

    return idle_instances


if __name__ == "__main__":
    result = find_idle_ec2()

    print("=== EC2 Idle Check ===")
    if result:
        for i in result:
            print(f"Idle EC2: {i['InstanceId']} ({i['InstanceType']})")
    else:
        print("No idle EC2 instances found.")