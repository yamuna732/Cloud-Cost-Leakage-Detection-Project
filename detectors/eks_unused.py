import boto3

ROLE_ARN = "arn:aws:iam::427684478761:role/CloudCostReadOnlyRole"
REGION = "ap-south-1"


def assume_role(role_arn):
    # SaaS EC2 IAM role provides base credentials automatically
    base_session = boto3.Session()
    sts = base_session.client("sts", region_name=REGION)

    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="EKSScan"
    )["Credentials"]

    # Session for customer account
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION
    )

    return session


def find_overprovisioned_k8s():
    """
    Detect EKS clusters that exist (potential cost).
    """
    session = assume_role(ROLE_ARN)
    eks = session.client("eks", region_name=REGION)

    findings = []

    clusters = eks.list_clusters()["clusters"]

    if not clusters:
        return findings

    for name in clusters:
        findings.append({
            "Cluster": name,
            "Namespace": "cluster",
            "Pod": "N/A",
            "Resource": "cluster_running"
        })

    return findings


# local / docker test
if __name__ == "__main__":
    result = find_overprovisioned_k8s()

    print("\n=== EKS Clusters ===")

    if not result:
        print("No EKS clusters found")
    else:
        for r in result:
            print(f"EKS Cluster: {r['Cluster']}")
