from prometheus_client import start_http_server, Counter
import time
import json
import os

migration_counter = Counter(
    "migration_event_total",
    "Total number of migration events",
    ["from_cluster", "to_cluster"]
)

CHECKPOINT_FILE = "checkpoints.json"
last_checkpoint_len = 0

def check_new_migrations():
    global last_checkpoint_len
    if not os.path.exists(CHECKPOINT_FILE):
        return

    with open(CHECKPOINT_FILE) as f:
        data = json.load(f)

    if len(data) > last_checkpoint_len:
        new = data[last_checkpoint_len:]
        for entry in new:
            f_cluster = entry.get("from")
            t_cluster = entry.get("to")
            migration_counter.labels(from_cluster=f_cluster, to_cluster=t_cluster).inc()
        last_checkpoint_len = len(data)

if __name__ == "__main__":
    print("Migration Exporter started at http://localhost:8001/metrics")
    start_http_server(8001)
    while True:
        check_new_migrations()
        time.sleep(5)
