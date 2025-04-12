import requests
import time
import random

# 여러분의 EC2 퍼블릭 IP로 바꾸세요!
SERVER_URL = "http://13.209.8.163:5000/receive-data"

def send_data():
    data = {
        "cluster": "agent-1",
        "carbon": round(random.uniform(10.0, 25.0), 2)  # 탄소값 랜덤 시뮬레이션
    }
    try:
        response = requests.post(SERVER_URL, json=data)
        print(f"[전송 성공] {data} → 응답: {response.status_code}")
    except Exception as e:
        print(f"[에러 발생] {e}")

if __name__ == "__main__":
    while True:
        send_data()
        time.sleep(5)  # 5초 간격 전송
