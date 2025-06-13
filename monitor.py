import subprocess

def get_cluster_cpu_memory_usage(context_name):
    try:
        result = subprocess.run(
            ["kubectl", "top", "pods", "--context", context_name, "--no-headers"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split("\n")
        total_millicores = 0
        total_memory_mib = 0

        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                # CPU 처리
                cpu = parts[1]
                if cpu.endswith("m"):
                    total_millicores += int(cpu[:-1])
                else:
                    total_millicores += int(cpu) * 1000

                # 메모리 처리
                mem = parts[2]
                if mem.endswith("Mi"):
                    total_memory_mib += int(mem[:-2])
                elif mem.endswith("Ki"):
                    total_memory_mib += int(mem[:-2]) // 1024  # KiB → MiB

        return total_millicores, total_memory_mib
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {context_name} metrics 실패: {e.stderr}")
        return 0, 0
