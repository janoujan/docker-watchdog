#!/usr/bin/env python3

import json
import csv
import argparse
import docker
from tabulate import tabulate

def get_container_stats(container):
    stats = container.stats(stream=False)
    mem_usage = stats['memory_stats']['usage'] / (1024 ** 2)  # en Mo
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0
    net_rx = 0
    net_tx = 0
    if 'networks' in stats:
        for iface in stats['networks'].values():
            net_rx += iface.get('rx_bytes', 0)
            net_tx += iface.get('tx_bytes', 0)
    return {
        'cpu_percent': round(cpu_percent, 2),
        'mem_MB': round(mem_usage, 2),
        'rx_KB': round(net_rx / 1024, 2),
        'tx_KB': round(net_tx / 1024, 2),
    }

def list_containers():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    result = []

    for container in containers:
        stats = {
            'Nom': container.name,
            'Image': container.image.tags[0] if container.image.tags else 'inconnu',
            'Statut': container.status
        }

        if container.status == 'running':
            usage = get_container_stats(container)
            stats.update({
                'CPU (%)': usage['cpu_percent'],
                'Mémoire (Mo)': usage['mem_MB'],
                'Rx (Ko)': usage['rx_KB'],
                'Tx (Ko)': usage['tx_KB']
            })
        else:
            stats.update({
                'CPU (%)': '-',
                'Mémoire (Mo)': '-',
                'Rx (Ko)': '-',
                'Tx (Ko)': '-'
            })

        result.append(stats)

    return result

if __name__ == "__main__":
    print("▶️ Attention attention Docker-watchdog va démarrer")

    parser = argparse.ArgumentParser(description="Surveille les conteneurs Docker.")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Format de sortie (table/json/csv)")
    args = parser.parse_args()

    try:
        containers_data = list_containers()

        if not containers_data:
            print("ℹ️ Aucun conteneur Docker trouvé.")
        elif args.format == "json":
            with open("export.json", "w") as f:
                json.dump(containers_data, f, indent=2)
            print("✅ Export JSON terminé : export.json")
        elif args.format == "csv":
            with open("export.csv", "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=containers_data[0].keys())
                writer.writeheader()
                writer.writerows(containers_data)
            print("✅ Export CSV terminé : export.csv")
        else:
            print(tabulate(containers_data, headers="keys", tablefmt="grid"))

    except Exception:
        import traceback
        traceback.print_exc()

    print("Bien bossé DockerWatchdog !!! et merci :D")
