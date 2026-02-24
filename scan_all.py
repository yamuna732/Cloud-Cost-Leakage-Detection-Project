from detectors.ec2_unused import find_idle_ec2
from detectors.rds_idle import find_idle_rds
from detectors.s3_forgotten import find_unused_s3
from detectors.eks_unused import find_overprovisioned_k8s

from monthly_report import generate_monthly_report, format_report
from email_sender import send_email


def build_shutdown_suggestions(ec2, rds, s3, k8s):
    suggestions = []

    if ec2:
        suggestions.append("EC2: Stop or terminate idle instances")

    if rds:
        suggestions.append("RDS: Stop idle DB instances or downgrade")

    if s3:
        suggestions.append("S3: Apply lifecycle or delete unused buckets")

    if k8s:
        suggestions.append("Kubernetes: Review cluster utilization or scale down")

    return "\n".join(suggestions)


def main():
    print("=== Cloud Cost Scan Started ===")

    # Run all scanners
    ec2 = find_idle_ec2()
    rds = find_idle_rds()
    s3 = find_unused_s3()
    k8s = find_overprovisioned_k8s()

    print(f"EC2 idle: {len(ec2)}")
    print(f"RDS idle: {len(rds)}")
    print(f"S3 unused: {len(s3)}")
    print(f"K8s over-provisioned: {len(k8s)}")

    # ---------- No leakage ----------
    if not any([ec2, rds, s3, k8s]):
        email_text = (
            "✅ Monthly Cloud Scan Result\n\n"
            "No unused or over-provisioned resources detected.\n"
            "Your cloud environment is well optimized."
        )

    # ---------- Leakage found ----------
    else:
        report = generate_monthly_report(ec2, rds, s3)
        email_text = format_report(report)

        email_text += "\n\n🔧 Auto-Shutdown Recommendations:\n"
        email_text += build_shutdown_suggestions(ec2, rds, s3, k8s)

        if k8s:
            email_text += "\n\n📦 EKS Clusters Detected:\n"
            for item in k8s:
                email_text += f"- {item.get('Cluster','cluster')}\n"

    # Send email
    send_email(email_text)

    print("=== Report emailed successfully ===")


if __name__ == "__main__":
    main()