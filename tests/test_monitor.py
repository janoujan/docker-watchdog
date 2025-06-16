import pytest
from unittest.mock import MagicMock, patch
from src.monitor import list_containers

@patch("src.monitor.docker.from_env")
def test_list_containers_basic(mock_from_env):
    # Création d'un faux conteneur
    fake_container = MagicMock()
    fake_container.name = "webapp"
    fake_container.image.tags = ["nginx:alpine"]
    fake_container.status = "exited"
    
    # Le client Docker simulé renvoie ce conteneur
    mock_client = MagicMock()
    mock_client.containers.list.return_value = [fake_container]
    mock_from_env.return_value = mock_client

    # Appel de la fonction testée
    list_containers()
    
    # Vérification que le conteneur a bien été listé
    mock_client.containers.list.assert_called_once_with(all=True)