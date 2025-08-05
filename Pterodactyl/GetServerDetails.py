# -----------------------------------------------------------------------------
# File Name   : GetServerDetails.py
# Description : Defines the get_server_details function to retrieve detailed
#               information about a specific server using the Pterodactyl
#               Admin or Client API, including allocations and variables.
#
# Author      : X
# Created On  : 05/08/2025
# Last Updated: 05/08/2025
# -----------------------------------------------------------------------------
from typing import Optional, Dict
import requests
from .PteroConnect import PteroConnect
from .ConsoleMessage import ConsoleMessage

log = ConsoleMessage()

def get_server_details(ptero: PteroConnect, server_identifier: int) -> Optional[Dict]:

    if not ptero.api_type:
        log.error("API type not detected. Cannot fetch server details.")
        return None

    # Admin expects numeric ID, client expects numeric ID
    if ptero.api_type == "admin":
        endpoint = f"/api/application/servers/{server_identifier}"
    elif ptero.api_type == "client":
        endpoint = f"/api/client/servers/{server_identifier}"
    else:
        log.error("Unsupported API type.")
        return None

    try:
        url = f"{ptero.panel_url}{endpoint}"
        response = requests.get(url, headers=ptero.headers, timeout=10)

        if response.status_code != 200:
            log.warning(f"Failed to retrieve server details: {response.status_code} - {response.text}")
            return None

        data = response.json()

        # Admin API: just return attributes
        if ptero.api_type == "admin":
            attr = data.get("attributes", {})
            return {
                "id": attr.get("id"),
                "uuid": attr.get("uuid"),
                "identifier": attr.get("identifier"),
                "name": attr.get("name"),
                "description": attr.get("description"),
                "limits": attr.get("limits"),
                "feature_limits": attr.get("feature_limits"),
                "suspended": attr.get("suspended"),
                "user_id": attr.get("user"),
                "node_id": attr.get("node"),
                "allocation_id": attr.get("allocation"),
                "nest_id": attr.get("nest"),
                "egg_id": attr.get("egg"),
                "container": attr.get("container"),
                "created_at": attr.get("created_at"),
                "updated_at": attr.get("updated_at")
            }

        # Client API: parse relationships and additional fields
        attr = data.get("attributes", {})
        relationships = attr.get("relationships", {})

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

        return {
            "id": attr.get("internal_id"),
            "uuid": attr.get("uuid"),
            "identifier": attr.get("identifier"),
            "name": attr.get("name"),
            "description": attr.get("description"),
            "status": attr.get("status"),
            "limits": attr.get("limits"),
            "feature_limits": attr.get("feature_limits"),
            "created_at": attr.get("created_at"),
            "updated_at": attr.get("updated_at"),
            "node": attr.get("node"),
            "server_owner": attr.get("server_owner"),
            "is_suspended": attr.get("is_suspended"),
            "is_installing": attr.get("is_installing"),
            "is_transferring": attr.get("is_transferring"),
            "docker_image": attr.get("docker_image"),
            "invocation": attr.get("invocation"),
            "allocations": allocations,
            "variables": variables
        }

    except requests.RequestException as e:
        log.error(f"Request error while retrieving server: {e}")
        return None
# -----------------------------------------------------------------------------
# End of File: GetServerDetails.py
# -----------------------------------------------------------------------------
