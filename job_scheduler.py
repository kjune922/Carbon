import subprocess
import yaml
import time

CLUSTERS = ["k3d-kr-seo-a", "k3d-kr-seo-b", "k3d-kr-seo-c", "k3d-kr-seo-d"]
JOB_TEMPLATE = "job-template.yaml"
DEPLOYED_JOBS = []

# 작업 큐: 각 작업은 name만 정의 (image는 템플릿에서 설정)
job_queue = [
    {"name": "job-a"},
    {"name": "job-b"},
    {"name": "job-c"}
]

def get_cluster_cpu(context):
    try:
        result = subprocess.check_output(
            ["kubectl", "--context", context, "top", "pods", "--no-headers"]
        )
        total_mcpu = 0
        for line in result.decode().splitlines():
            cpu = line.split()[1]
            if cpu.endswith("m"):
                total_mcpu += int(cpu[:-1])
        return total_mcpu
    except:
        return 0

def calculate_carbon(cpu):
    return round(cpu * 0.000475, 3)

def select_best_cluster():
    scores = []
    for ctx in CLUSTERS:
        cpu = get_cluster_cpu(ctx)
        carbon = calculate_carbon(cpu)
        scores.append((carbon, ctx))
    scores.sort()
    return scores[0][1]  # 가장 낮은 탄소 클러스터 반환

def deploy_job_to_cluster(job_name, context):
    with open(JOB_TEMPLATE) as f:
        spec = yaml.safe_load(f)
    spec["metadata"]["name"] = job_name
    spec["spec"]["template"]["metadata"]["labels"]["app"] = job_name
    temp_file = f"{job_name}.yaml"
    with open(temp_file, "w") as f:
        yaml.dump(spec, f)
    subprocess.run(["kubectl", "--context", context, "apply", "-f", temp_file])
    print(f"✅ Job '{job_name}' → {context}")
    DEPLOYED_JOBS.append((job_name, context))

if __name__ == "__main__":
    print("작업 큐 배포 시작")
    while job_queue:
        job = job_queue.pop(0)
        best_cluster = select_best_cluster()
        deploy_job_to_cluster(job["name"], best_cluster)
        time.sleep(2)
    print("📦 모든 작업 배포 완료")
