from detectors.rds_idle import find_idle_rds

data = find_idle_rds()

if not data:
    print("No idle RDS instances")
else:
    for db in data:
        print(db)