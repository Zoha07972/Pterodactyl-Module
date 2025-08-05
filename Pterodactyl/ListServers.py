# -----------------------------------------------------------------------------
# File Name   : ListServers.py
# Description : Provides functionality to list and count servers from a
#               Pterodactyl panel using either the Admin or Client API.
#               Includes pagination support and conditional data parsing.
#
# Author      : X
# Created On  : 05/08/2025
# Last Updated: 05/08/2025
# -----------------------------------------------------------------------------

from typing import List, Dict, Optional
from .PteroConnect import PteroConnect
from .ConsoleMessage import ConsoleMessage
import requests

log = ConsoleMessage()

def list_servers(ptero: PteroConnect, search: Optional[str] = None) -> List[Dict]:

    if not ptero.api_type:
        log.error("API type not detected. Cannot list servers.")
        return []

    all_servers = []
    page = 1

    # Set base endpoint
    if ptero.api_type == "admin":
        endpoint = "/api/application/servers"
    elif ptero.api_type == "client":
        endpoint = "/api/client"
    else:
        log.error("Unsupported API type.")
        return []

    while True:
        url = f"{ptero.panel_url}{endpoint}?page={page}"
        if ptero.api_type == "admin" and search:
            url += f"&filter[name]={search}"

        try:
            response = requests.get(url, headers=ptero.headers, timeout=10)
            if response.status_code != 200:
                log.warning(f"Failed to list servers: {response.status_code} - {response.text}")
                break

            data = response.json()
            servers = data.get("data", [])

            for server in servers:
                attr = server.get("attributes", {})
                relationships = attr.get("relationships", {}) if ptero.api_type == "client" else {}

                # Extract allocations (client only)
                allocations = []
                for alloc in relationships.get("allocations", {}).get("data", []):
                    a = alloc.get("attributes", {})
                    allocations.append({
                        "id": a.get("id"),
                        "ip": a.get("ip"),
                        "ip_alias": a.get("ip_alias"),
                        "port": a.get("port"),
                        "notes": a.get("notes"),
                        "is_default": a.get("is_default"),
                    })

                # Extract variables (client only)
                variables = []
                for var in relationships.get("variables", {}).get("data", []):
                    v = var.get("attributes", {})
                    variables.append({
                        "name": v.get("name"),
                        "description": v.get("description"),
                        "env_variable": v.get("env_variable"),
                        "default_value": v.get("default_value"),
                        "server_value": v.get("server_value"),
                        "is_editable": v.get("is_editable"),
                        "rules": v.get("rules"),
                    })

                server_obj = {
                    "id": attr.get("internal_id") if ptero.api_type == "client" else attr.get("id"),
                    "uuid": attr.get("uuid"),
                    "identifier": attr.get("identifier"),
                    "name": attr.get("name"),
                    "description": attr.get("description"),
                    "status": attr.get("status"),
                    "limits": attr.get("limits"),
                    "feature_limits": attr.get("feature_limits"),
                    "created_at": attr.get("created_at"),
                    "updated_at": attr.get("updated_at")
                }

                if ptero.api_type == "admin":
                    server_obj.update({
                        "suspended": attr.get("suspended"),
                        "user_id": attr.get("user"),
                        "node_id": attr.get("node"),
                        "allocation_id": attr.get("allocation"),
                        "nest_id": attr.get("nest"),
                        "egg_id": attr.get("egg"),
                        "container": attr.get("container"),
                    })
                else:
                    server_obj.update({
                        "node": attr.get("node"),
                        "server_owner": attr.get("server_owner"),
                        "is_suspended": attr.get("is_suspended"),
                        "is_installing": attr.get("is_installing"),
                        "is_transferring": attr.get("is_transferring"),
                        "docker_image": attr.get("docker_image"),
                        "invocation": attr.get("invocation"),
                        "allocations": allocations,
                        "variables": variables,
                    })

                all_servers.append(server_obj)

            # Pagination logic for both admin and client
            pagination = data.get("meta", {}).get("pagination", {})
            if not pagination:
                break  # No more pages or pagination info

            total_pages = pagination.get("total_pages", 1)
            if ptero.debug:
                log.debug(f"Fetched page {page} of {total_pages}")

            if page >= total_pages:
                break

            page += 1

        except requests.RequestException as e:
            log.error(f"Error fetching server list: {e}")
            break


    return all_servers


def get_total_servers(ptero: PteroConnect, search: Optional[str] = None) -> int:
    total = len(list_servers(ptero, search))
    log.info(f"Total servers found: {total}")
    return total
# -----------------------------------------------------------------------------
# End of File: ListServers.py
# -----------------------------------------------------------------------------
