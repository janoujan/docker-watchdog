#!/usr/bin/env python3

print("test_monitor demarre")

import pytest
from monitor import list_containers
from unittest.mock import MagicMock, patch

@patch("monitor.docker.from_env")  # 👈 Correction ici
def test_list_containers_basic(mock_from_env):
    fake_container = MagicMock()
    fake_container.name = "webapp"
    fake_container.image.tags = ["nginx:alpine"]
    fake_container.status = "exited"

    mock_client = MagicMock()
    mock_client.containers.list.return_value = [fake_container]
    mock_from_env.return_value = mock_client

    list_containers()

    mock_client.containers.list.assert_called_once_with(all=True)

    print("test_monitor a bien bossé, bye bye !!!")
