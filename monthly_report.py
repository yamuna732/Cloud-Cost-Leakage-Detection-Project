USD_TO_INR = 83

EC2_PRICING = {
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
}

RDS_PRICING = {
    "db.t3.micro": 0.017,
    "db.t3.small": 0.034,
    "db.t3.medium": 0.068,
}

S3_PRICE_PER_GB = 0.023


def generate_monthly_report(ec2, rds, s3):
    report = {
        "ec2": [],
        "rds": [],
        "s3": [],
        "total_savings_inr": 0,
    }

    total = 0

    # EC2
    for i in ec2:
        itype = i.get("InstanceType", "t3.micro")
        price = EC2_PRICING.get(itype, 0.02)
        monthly = price * 730 * USD_TO_INR

        report["ec2"].append({
            "id": i["InstanceId"],
            "type": itype,
            "monthly_inr": round(monthly),
        })

        total += monthly

    # RDS
    for db in rds:
        dtype = db.get("DBInstanceClass", "db.t3.micro")
        price = RDS_PRICING.get(dtype, 0.03)
        monthly = price * 730 * USD_TO_INR

        report["rds"].append({
            "id": db["DBInstanceIdentifier"],
            "type": dtype,
            "monthly_inr": round(monthly),
        })

        total += monthly

    # S3
    for b in s3:
        size = b.get("SizeGB", 0)
        monthly = size * S3_PRICE_PER_GB * USD_TO_INR

        report["s3"].append({
            "bucket": b["Name"],
            "size_gb": size,
            "monthly_inr": round(monthly),
        })

        total += monthly

    report["total_savings_inr"] = round(total)
    return report


def format_report(report):
    lines = []
    lines.append("📊 Monthly Cloud Savings Report\n")

    if report["ec2"]:
        lines.append("EC2 Idle:")
        for e in report["ec2"]:
            lines.append(f"- {e['id']} ({e['type']}) ₹{e['monthly_inr']}")
        lines.append("")

    if report["rds"]:
        lines.append("RDS Idle:")
        for r in report["rds"]:
            lines.append(f"- {r['id']} ({r['type']}) ₹{r['monthly_inr']}")
        lines.append("")

    if report["s3"]:
        lines.append("S3 Unused:")
        for s in report["s3"]:
            lines.append(f"- {s['bucket']} ({s['size_gb']} GB) ₹{s['monthly_inr']}")
        lines.append("")

    lines.append(f"💰 Total Potential Monthly Savings: ₹{report['total_savings_inr']}")

    return "\n".join(lines)