import os
from storage.tunnel_code import TunnelCode

from flask import current_app

def file_storage_tunnel_exist(filename: str, tunnel: TunnelCode) -> bool:
    storage_path: str = current_app.config["STORAGE_PATH"]
    path = f"{storage_path}/{tunnel.value}/{filename}"
    return os.path.exists(path)


def file_storage_tunnel_read(filename: str, tunnel: TunnelCode) -> str:
    storage_path: str = current_app.config["STORAGE_PATH"]
    path = f"{storage_path}/{tunnel.value}/{filename}"
    if file_storage_tunnel_exist(filename, tunnel):
        with open(path, "r") as file:
            return file.read()
    else:
        return ""


def byte_storage_tunnel_read(filename: str, tunnel: TunnelCode) -> bytes:
    storage_path: str = current_app.config["STORAGE_PATH"]
    path = f"{storage_path}/{tunnel.value}/{filename}"
    if file_storage_tunnel_exist(filename, tunnel):
        with open(path, "rb") as file:
            return file.read()
    else:
        return 0


def file_storage_tunnel_write(filename: str, data: str, tunnel: TunnelCode) -> None:
    storage_path: str = current_app.config["STORAGE_PATH"]
    path = f"{storage_path}/{tunnel.value}/{filename}"
    with open(path, "w") as file:
        file.write(data)
        file.close()


def byte_storage_tunnel_write(filename: str, data, tunnel: TunnelCode) -> None:
    storage_path: str = current_app.config["STORAGE_PATH"]
    path = f"{storage_path}/{tunnel.value}/{filename}"
    with open(path, "wb") as file:
        file.write(data)
        file.close()


def file_storage_tunnel_del(filename: str, tunnel: TunnelCode) -> str:
    storage_path: str = current_app.config["STORAGE_PATH"]
    path = f"{storage_path}/{tunnel.value}/{filename}"
    if file_storage_tunnel_exist(filename, tunnel):
        os.remove(path)
    else:
        return ""
