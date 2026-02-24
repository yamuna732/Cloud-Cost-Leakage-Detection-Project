import boto3

ROLE_ARN = "arn:aws:iam::427684478761:role/CloudCostReadOnlyRole"
REGION = "ap-south-1"


def assume_role(role_arn):
    base_session = boto3.Session(profile_name="saas")
    sts = base_session.client("sts")

    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="EKSScan"
    )["Credentials"]

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
    Later can extend to pod-level overprovisioning.
    """
    session = assume_role(ROLE_ARN)
    eks = session.client("eks")

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


# local test
if __name__ == "__main__":
    result = find_overprovisioned_k8s()

    print("\n=== EKS Clusters ===")

    if not result:
        print("No EKS clusters found")
    else:
        for r in result:
            print(f"EKS Cluster: {r['Cluster']}")