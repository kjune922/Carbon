from prometheus_client import start_http_server, Gauge
import subprocess
import json
import time

# Prometheus 메트릭 정의
carbon_gauge = Gauge("carbon_emission_gco2", "Carbon Emission in gCO2eq", ["cluster"])

# 모니터링 대상 클러스터
clusters = ["k3d-kr-seo-a", "k3d-kr-seo-b", "k3d-kr-seo-c", "k3d-kr-seo-d"]

# 탄소 환산식 
def calculate_carbon(mcpu):
    return round(mcpu * 0.000475, 3)

# 각 클러스터에서 mCPU 수집
def get_cluster_mcpu(context):
    try:
        result = subprocess.check_output([
            "kubectl", "--context", context, "top", "pods", "--no-headers"
        ])
        total_mcpu = 0
        for line in result.decode().splitlines():
            cpu_str = line.split()[1]
            if cpu_str.endswith("m"):
                total_mcpu += int(cpu_str[:-1])
        return total_mcpu
    except:
        return 0

# main 루프
if __name__ == "__main__":
    # Prometheus에서 수집할 수 있도록 /metrics HTTP 서버 시작
    start_http_server(8000)
    print("✅ carbon_exporter running at http://localhost:8000/metrics")

    while True:
        for cluster in clusters:
            mcpu = get_cluster_mcpu(cluster)
            gco2 = calculate_carbon(mcpu)
            carbon_gauge.labels(cluster=cluster).set(gco2)
            print(f"{cluster}: {mcpu} mCPU → {gco2} gCO₂eq")
        time.sleep(10)
