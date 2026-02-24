import boto3
from detectors.ec2_unused import detect_unused_ec2

REGION = "ap-south-1"
PROFILE = "saas"   # your SaaS AWS account

# Create session
session = boto3.Session(profile_name=PROFILE)

# Run detection
results = detect_unused_ec2(session, REGION)

# Print output
print(f"\nUnused EC2 Instances in {REGION}:\n")

if not results:
    print("No unused EC2 instances found ✅")
else:
    for r in results:
        print(
            f"{r['InstanceId']}  |  {r['Region']}  |  {r['Reason']}"
        )