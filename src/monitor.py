#!/usr/bin/env python3

print("▶️ monitor.py démarre")

import docker
from tabulate import tabulate


def get_container_stats(container):
      """
        Retourne un dictionnaire de statistiques système pour un conteneur en cours d'exécution.
      """
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
    """
    Liste les conteneurs Docker et affiche leurs statistiques.
    """
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

    print(tabulate(result, headers='keys', tablefmt='grid'))

    '''
     if __name__ == "__main__":
      for name, image, status in list_containers():
        print(f"{name:20} | {image:30} | {status}")
    '''
list_containers() 
try:
    list_containers()
except Exception:
    import traceback; traceback.print_exc() 

print("bye bye monitor.py et merci")