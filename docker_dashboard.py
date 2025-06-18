import streamlit as st
import docker
from time import sleep

def get_container_stats(container):
    """Récupère les statistiques d'utilisation d'un conteneur Docker."""
    try:
        stats = container.stats(stream=False)
        mem_usage = stats['memory_stats']['usage'] / (1024 ** 2)  # en Mo
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0
        net_rx = sum(iface.get('rx_bytes', 0) for iface in stats.get('networks', {}).values()) / 1024
        net_tx = sum(iface.get('tx_bytes', 0) for iface in stats.get('networks', {}).values()) / 1024
        return {
            'cpu_percent': round(cpu_percent, 2),
            'mem_MB': round(mem_usage, 2),
            'net_rx_KB': round(net_rx, 2),
            'net_tx_KB': round(net_tx, 2)
        }
    except Exception as e:
        st.error(f"Erreur lors de la récupération des statistiques pour le conteneur {container.name}: {e}")
        return {'cpu_percent': 0, 'mem_MB': 0, 'net_rx_KB': 0, 'net_tx_KB': 0}

def get_status_indicator(status):
    """Retourne un indicateur visuel basé sur l'état du conteneur."""
    status_map = {
        'running': ("🟢", "green", "En cours d'exécution"),
        'exited': ("🔴", "red", "Arrêté"),
        'created': ("🟠", "orange", "Créé"),
        'restarting': ("🔄", "blue", "Redémarrage"),
        'paused': ("⏸️", "gray", "En pause"),
        'dead': ("☠️", "black", "Mort")
    }
    return status_map.get(status, ("🟡", "yellow", "Autre état"))

def get_containers_data():
    """Récupère les données de tous les conteneurs."""
    client = docker.from_env()
    return client.containers.list(all=True)

def display_container(container):
    """Affiche les informations d'un conteneur."""
    container.reload()
    status_indicator, status_color, status_text = get_status_indicator(container.status)

    #with st.expander(f"{status_indicator} **{container.name}** ({status_text})", expanded=True):
    with st.expander(f"{status_indicator} **{container.name}** ({status_text})", expanded=True):
      col1, col2 = st.columns(2)
    with col1:
      st.markdown(f"**Image:** {container.image.tags[0] if container.image.tags else 'unknown'}")
      st.markdown(f"**Status:** <span style='color:{status_color}'>{container.status}</span>", unsafe_allow_html=True)
    with col2:
            if container.status == 'running':
                usage = get_container_stats(container)
                st.markdown(f"**CPU Usage:** {usage['cpu_percent']}%")
                st.progress(usage['cpu_percent'])
                st.markdown(f"**Memory Usage:** {usage['mem_MB']} MB")
                st.progress(min(usage['mem_MB'] / 100, 1.0))  # Supposons une mémoire max de 100MB pour l'exemple
                st.markdown(f"**Network RX:** {usage['net_rx_KB']} KB")
                st.markdown(f"**Network TX:** {usage['net_tx_KB']} KB")

        # Boutons d'action avec clés uniques utilisant container.id et l'action
            col_action1, col_action2, col_action3 = st.columns(3)
    with col_action1:
            if container.status != 'running':
                if st.button(f"Démarrer", key=f"start_{container.id}"):
                    container.start()
                    st.success(f"Conteneur {container.name} démarré")
                    sleep(1)
                    st.rerun()
            else:
                st.markdown("Déjà en cours d'exécution")

    with col_action2:
            if container.status == 'running':
                if st.button(f"Arrêter", key=f"stop_{container.id}"):
                    container.stop()
                    st.success(f"Conteneur {container.name} arrêté")
                    sleep(1)
                    st.rerun()
            else:
                st.markdown("Déjà arrêté")

    with col_action3:
            if st.button(f"Supprimer", key=f"remove_{container.id}"):
                container.remove()
                st.success(f"Conteneur {container.name} supprimé")
                sleep(1)
                st.rerun()

def main():
    st.markdown("""
    <style>
    /* Applique une bordure turquoise à tous les expanders */
    .st-expander {
        border: 2px solid #4BF5FF !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

    st.title("Docker Containers Dashboard")

    # Ajouter un bouton de rafraîchissement manuel dans la sidebar
    if st.sidebar.button("↻ Rafraîchir"):
        st.rerun()

    # Sélecteur d'intervalle de rafraîchissement automatique
    refresh_interval = st.sidebar.selectbox(
        "Intervalle de rafraîchissement automatique",
        options=[0, 5, 10, 15, 30, 60],
        index=1,  # 5 secondes par défaut
        format_func=lambda x: f"{x} secondes" if x > 0 else "Désactivé"
    )

    # Ajouter un sélecteur pour filtrer les conteneurs par état
    status_filter = st.sidebar.multiselect(
        "Filtrer par état",
        options=["En cours d'exécution", "Arrêté", "Créé", "Autre état", "Tous"],
        default=["Tous"]
    )

    # Obtenir et afficher les données des conteneurs
    containers = get_containers_data()

    if not containers:
        st.warning("Aucun conteneur Docker trouvé.")
    else:
        for container in containers:
            try:
                status_indicator, _, status_text = get_status_indicator(container.status)

                # Appliquer le filtre
                if "Tous" not in status_filter:
                    if status_text not in status_filter:
                        continue

                display_container(container)
            except Exception as e:
                st.error(f"Erreur avec le conteneur {container.name}: {str(e)}")

    # Rafraîchissement automatique
    if refresh_interval > 0:
        sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
