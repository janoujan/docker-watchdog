import streamlit as st
import docker

def get_container_stats(container):
    stats = container.stats(stream=False)
    mem_usage = stats['memory_stats']['usage'] / (1024 ** 2)  # en Mo
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0
    return {
        'cpu_percent': round(cpu_percent, 2),
        'mem_MB': round(mem_usage, 2)
    }

def main():
    st.title("Docker Container Dashboard")

    client = docker.from_env()
    containers = client.containers.list(all=True)

    for container in containers:
        st.subheader(container.name)
        st.write(f"Image: {container.image.tags[0] if container.image.tags else 'inconnu'}")
        st.write(f"Status: {container.status}")

        if container.status == 'running':
            stats = get_container_stats(container)
            st.write(f"CPU Usage: {stats['cpu_percent']}%")
            st.write(f"Memory Usage: {stats['mem_MB']} MB")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Start {container.name}"):
                container.start()
                st.success(f"Container {container.name} started")
        with col2:
            if st.button(f"Stop {container.name}"):
                container.stop()
                st.success(f"Container {container.name} stopped")
        with col3:
            if st.button(f"Remove {container.name}"):
                container.remove()
                st.success(f"Container {container.name} removed")

if __name__ == "__main__":
    main()
