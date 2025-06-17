import argparse
import csv
import docker
import json
import sqlite3
import statistics
import time
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from tabulate import tabulate
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import streamlit as st
import os

# Connexion à la base de données SQLite
def setup_database():
    conn = sqlite3.connect('container_events.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS container_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        container_name TEXT NOT NULL,
        event_type TEXT NOT NULL,
        event_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    return conn

# Surveillance des événements des conteneurs
def monitor_container_events(client, conn):
    cursor = conn.cursor()
    for event in client.events():
        if 'status' in event:
            container_name = event['Actor']['Attributes']['name']
            event_type = event['status']
            log_event(cursor, container_name, event_type)

def log_event(cursor, container_name, event_type):
    cursor.execute('''
    INSERT INTO container_events (container_name, event_type)
    VALUES (?, ?)
    ''', (container_name, event_type))
    cursor.connection.commit()

# Analyse des statistiques des conteneurs
def analyze_container_stats(client):
    history = {}
    while True:
        containers = client.containers.list()
        anomalies, history = detect_anomalies(containers, history)
        for anomaly in anomalies:
            print(anomaly)
        time.sleep(60)

def detect_anomalies(containers, history):
    anomalies = []
    for container in containers:
        stats = get_container_stats(container)
        container_name = container.name
        cpu_percent = stats['cpu_percent']
        mem_MB = stats['mem_MB']

        if container_name in history:
            cpu_history = history[container_name]['cpu']
            mem_history = history[container_name]['mem']

            cpu_mean = statistics.mean(cpu_history)
            mem_mean = statistics.mean(mem_history)

            cpu_std = statistics.stdev(cpu_history) if len(cpu_history) > 1 else 0
            mem_std = statistics.stdev(mem_history) if len(mem_history) > 1 else 0

            if cpu_percent > cpu_mean + 2 * cpu_std:
                anomalies.append(f"High CPU usage detected in container {container_name}: {cpu_percent}%")
            if mem_MB > mem_mean + 2 * mem_std:
                anomalies.append(f"High memory usage detected in container {container_name}: {mem_MB} MB")

        history[container_name] = {
            'cpu': history.get(container_name, {}).get('cpu', []) + [cpu_percent],
            'mem': history.get(container_name, {}).get('mem', []) + [mem_MB]
        }

    return anomalies, history

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

# Visualisation des connexions réseau
def visualize_network_connections(client):
    G = nx.Graph()
    for container in client.containers.list():
        container.reload()  # Assurez-vous que les données du conteneur sont à jour
        container_name = container.name
        G.add_node(container_name)

        # Ajoutez des connexions basées sur les réseaux partagés
        for network in container.attrs['NetworkSettings']['Networks']:
            G.add_edge(container_name, network)

    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()

# Génération de rapports hebdomadaires et export en .html et .pdf
def generate_weekly_report(client, output_html, output_pdf):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')

    containers = client.containers.list(all=True)
    report_data = []

    for container in containers:
        stats = get_container_stats(container)
        report_data.append({
            'Nom': container.name,
            'Image': container.image.tags[0] if container.image.tags else 'inconnu',
            'Statut': container.status,
            'CPU (%)': stats['cpu_percent'],
            'Mémoire (Mo)': stats['mem_MB'],
            'Rx (Ko)': stats['rx_KB'],
            'Tx (Ko)': stats['tx_KB']
        })

    html_out = template.render(containers=report_data)

    with open(output_html, 'w') as f:
        f.write(html_out)

    HTML(string=html_out).write_pdf(output_pdf)

    html_out = template.render(containers=report_data)
    HTML(string=html_out).write_pdf('weekly_report.pdf')

# Interaction directe avec les conteneurs
def container_interaction_dashboard(client):
    st.title("Docker Container Interaction Dashboard")

    containers = client.containers.list(all=True)
    for container in containers:
        st.subheader(container.name)
        if st.button(f"Start {container.name}"):
            container.start()
        if st.button(f"Stop {container.name}"):
            container.stop()
        if st.button(f"Remove {container.name}"):
            container.remove()

if __name__ == "__main__":
    print("▶️ Attention attention Docker-watchdog va démarrer")

    parser = argparse.ArgumentParser(description="Surveille les conteneurs Docker.")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Format de sortie (table/json/csv)")
    args = parser.parse_args()

    try:
        client = docker.from_env()
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

        # Setup database and start monitoring events and analyzing stats
        conn = setup_database()
        monitor_container_events(client, conn)
        analyze_container_stats(client)

        # Visualize network connections
        visualize_network_connections(client)

        # Generate weekly report
        generate_weekly_report(client, 'weekly_report.html', 'weekly_report.pdf')

        # Start interaction dashboard
        container_interaction_dashboard(client)

    except Exception as e:
        import traceback
        traceback.print_exc()
