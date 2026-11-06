"""Fetch ALB and ECS metrics from CloudWatch for one time window (chapter 67 and 71).

!! NEEDS AWS CREDENTIALS and READ-ONLY permissions. !!
The IAM identity only needs cloudwatch:GetMetricData. It never writes anything.
This file is compile-checked only (python -m py_compile). Do not run it against
an account unless you own it and have approval. The handbook does not deploy to AWS.

Example (replace every value with your own; these are placeholders):

    python cloudwatch_pull.py --region eu-west-1 \
      --alb-lb app/taskflow-alb/50dc6c495c0c9188 \
      --target-group targetgroup/task-service/73e2d6bc24d8a067 \
      --cluster taskflow --service task-service \
      --start 2026-11-06T10:00:00Z --end 2026-11-06T10:15:00Z \
      --out cloudwatch.json

Requires Python 3.11+ (for ISO 8601 "Z" timestamps) and boto3.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import boto3


def build_queries(lb: str, target_group: str, cluster: str, service: str, period: int) -> list[dict]:
    """Metric queries for GetMetricData. Ids must start with a lowercase letter."""
    alb_dims_tg = [
        {"Name": "LoadBalancer", "Value": lb},
        {"Name": "TargetGroup", "Value": target_group},
    ]
    ecs_dims = [
        {"Name": "ClusterName", "Value": cluster},
        {"Name": "ServiceName", "Value": service},
    ]

    def query(qid: str, namespace: str, name: str, dims: list[dict], stat: str) -> dict:
        return {
            "Id": qid,
            "MetricStat": {
                "Metric": {"Namespace": namespace, "MetricName": name, "Dimensions": dims},
                "Period": period,
                "Stat": stat,
            },
            "ReturnData": True,
        }

    return [
        # Application Load Balancer (AWS/ApplicationELB)
        query("alb_target_rt_p95", "AWS/ApplicationELB", "TargetResponseTime", alb_dims_tg, "p95"),
        query("alb_req_per_target", "AWS/ApplicationELB", "RequestCountPerTarget",
              [{"Name": "TargetGroup", "Value": target_group}], "Sum"),
        query("alb_target_5xx", "AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", alb_dims_tg, "Sum"),
        query("alb_elb_5xx", "AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count",
              [{"Name": "LoadBalancer", "Value": lb}], "Sum"),
        query("alb_unhealthy", "AWS/ApplicationELB", "UnHealthyHostCount", alb_dims_tg, "Maximum"),
        # ECS Container Insights (ECS/ContainerInsights). CpuUtilized is in CPU units, not percent.
        query("ecs_cpu_units", "ECS/ContainerInsights", "CpuUtilized", ecs_dims, "Average"),
        query("ecs_memory_mib", "ECS/ContainerInsights", "MemoryUtilized", ecs_dims, "Average"),
        query("ecs_running", "ECS/ContainerInsights", "RunningTaskCount", ecs_dims, "Maximum"),
        query("ecs_desired", "ECS/ContainerInsights", "DesiredTaskCount", ecs_dims, "Maximum"),
    ]


def fetch(region: str, queries: list[dict], start: datetime, end: datetime) -> dict:
    client = boto3.client("cloudwatch", region_name=region)
    paginator = client.get_paginator("get_metric_data")
    series: dict[str, dict] = {q["Id"]: {"timestamps": [], "values": []} for q in queries}

    # GetMetricData returns a NextToken for big result sets. The paginator follows it.
    for page in paginator.paginate(
        MetricDataQueries=queries,
        StartTime=start,
        EndTime=end,
        ScanBy="TimestampAscending",
    ):
        for result in page["MetricDataResults"]:
            bucket = series[result["Id"]]
            bucket["timestamps"].extend(t.isoformat() for t in result["Timestamps"])
            bucket["values"].extend(result["Values"])
    return series


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull ALB and ECS metrics (read-only).")
    parser.add_argument("--region", required=True)
    parser.add_argument("--alb-lb", required=True, help="e.g. app/taskflow-alb/50dc6c495c0c9188")
    parser.add_argument("--target-group", required=True, help="e.g. targetgroup/task-service/73e2d6bc24d8a067")
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--start", required=True, help="ISO 8601 UTC, e.g. 2026-11-06T10:00:00Z")
    parser.add_argument("--end", required=True, help="ISO 8601 UTC, e.g. 2026-11-06T10:15:00Z")
    parser.add_argument("--period", type=int, default=60, help="Seconds per data point (default 60)")
    parser.add_argument("--out", type=Path, default=Path("cloudwatch.json"))
    args = parser.parse_args()

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)
    if end <= start:
        parser.error("--end must be after --start")

    queries = build_queries(args.alb_lb, args.target_group, args.cluster, args.service, args.period)
    series = fetch(args.region, queries, start, end)
    args.out.write_text(json.dumps(series, indent=2), encoding="utf-8")
    print(f"wrote {args.out} ({len(queries)} series)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
