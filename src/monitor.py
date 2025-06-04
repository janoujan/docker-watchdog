import docker
 
def list_containers():
 """
 Liste les conteneurs Docker présents sur la machine.
 Retourne une liste de tuples : (nom, image, statut)
 """
 client = docker.from_env()
 containers = client.containers.list(all=True)
 return [(c.name, c.image.tags[0] if c.image.tags else "inconnu", c.status)
   for c in containers]
 if __name__ == "__main__":
   for name, image, status in list_containers():
     print(f"{name:20} | {image:30} | {status}")

     