# migration_manager.py (확장된 버전: 체크포인트 저장 포함)

import subprocess
import time
import yaml
import json
import os

# --- 설정 ---
TARGET_POD_NAME = "web"
NAMESPACE = "default"
SOURCE_CLUSTER = "k3d-kr-seo-a"
DEST_CLUSTER = "k3d-kr-seo-b"

BACKUP_FILE = "pod-backup.yaml"
CHECKPOINT_FILE = "checkpoints.json"

# --- 함수: 실행 결과 가져오기 ---
def run(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()

# --- 체크포인트 저장 ---
def save_checkpoint():
    checkpoint = {
        "pod": TARGET_POD_NAME,
        "namespace": NAMESPACE,
        "source": SOURCE_CLUSTER,
        "dest": DEST_CLUSTER,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
    else:
        data = []

    data.append(checkpoint)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("📌 체크포인트 저장 완료")

# --- 1. 현재 실행 중인 Pod yaml 추출 ---
def backup_pod_yaml():
    cmd = ["kubectl", "--context", SOURCE_CLUSTER, "get", "pod", TARGET_POD_NAME,
           "-n", NAMESPACE, "-o", "yaml"]
    yaml_data = run(cmd)
    with open(BACKUP_FILE, "w") as f:
        f.write(yaml_data)
    print("✅ Pod YAML 백업 완료")

# --- 2. 불필요한 필드 제거 (metadata.uid, resourceVersion 등) ---
def clean_yaml():
    with open(BACKUP_FILE) as f:
        pod = yaml.safe_load(f)

    for key in ["uid", "resourceVersion", "selfLink", "creationTimestamp"]:
        pod["metadata"].pop(key, None)

    pod["metadata"].pop("annotations", None)
    pod["status"] = {}  # 상태 제거

    with open(BACKUP_FILE, "w") as f:
        yaml.dump(pod, f)
    print("🧹 YAML 정리 완료")

# --- 3. 다른 클러스터에 재배포 ---
def deploy_to_new_cluster():
    cmd = ["kubectl", "--context", DEST_CLUSTER, "apply", "-f", BACKUP_FILE]
    print(run(cmd))
    print("🚀 새 클러스터에 배포 완료")

# --- 4. 기존 클러스터에서 삭제 ---
def delete_old_pod():
    cmd = ["kubectl", "--context", SOURCE_CLUSTER, "delete", "pod", TARGET_POD_NAME, "-n", NAMESPACE]
    print(run(cmd))
    print("🗑️ 기존 클러스터에서 Pod 삭제 완료")

# --- 메인 실행 ---
if __name__ == "__main__":
    backup_pod_yaml()
    clean_yaml()
    deploy_to_new_cluster()
    save_checkpoint()
    time.sleep(2)
    delete_old_pod()
