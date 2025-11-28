#!usrbinenv python

Compare two Google Tag Manager containers (field-level) and export differences to CSV.

Dependencies (install via pip)
    pip install google-api-python-client google-auth google-auth-oauthlib

Usage
    1. Set GTM_OAUTH_PATH env var OR edit CRED_PATH default.
    2. Set ACCOUNT_NAME and container names in the main() section.
    3. Run
        python gtm_container_diff.py


from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# --- Configuration  auth paths ------------------------------------------------

SCOPES = [httpswww.googleapis.comauthtagmanager.readonly]

# Either set env vars or hard-code a fallback path
CRED_PATH = Path(os.environ.get(GTM_OAUTH_PATH, pathtoyourclient_secret.json))
TOKEN_PATH = Path(os.environ.get(GTM_TOKEN_PATH, token.json))


# --- Auth & service helpers ----------------------------------------------------


def get_gtm_service()
    Return an authenticated GTM API service client.
    creds = None

    if TOKEN_PATH.exists()
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid
        if creds and creds.expired and creds.refresh_token
            creds.refresh(Request())
        else
            if not CRED_PATH.exists()
                raise FileNotFoundError(
                    fClient secret file not found at {CRED_PATH}. 
                    Set GTM_OAUTH_PATH or update CRED_PATH.
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CRED_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json())

    return build(tagmanager, v2, credentials=creds)


# --- GTM lookup helpers --------------------------------------------------------


def find_account_id(service, account_name str) - str
    Return the accountId for a given account display name.
    result = service.accounts().list().execute()
    accounts = result.get(account, [])

    for acc in accounts
        if acc.get(name) == account_name or acc.get(displayName) == account_name
            return acc[accountId]

    raise ValueError(fGTM account not found with name {account_name!r})


def find_container(service, account_id str, container_name str) - Dict[str, Any]
    Return the container dict for a given name within an account.
    parent = faccounts{account_id}
    result = service.accounts().containers().list(parent=parent).execute()
    containers = result.get(container, [])

    for c in containers
        if c.get(name) == container_name
            return c

    raise ValueError(
        fGTM container not found with name {container_name!r} in account {account_id}
    )


def find_default_workspace(service, container_path str) - Dict[str, Any]
    Return the default workspace (by name or first) for a container.
    result = (
        service.accounts()
        .containers()
        .workspaces()
        .list(parent=container_path)
        .execute()
    )
    workspaces = result.get(workspace, [])
    if not workspaces
        raise RuntimeError(fNo workspaces found for container {container_path})

    for ws in workspaces
        if ws.get(name, ).lower() == default workspace
            return ws

    # Fall back to the first workspace if no 'Default Workspace' by name
    return workspaces[0]


# --- Snapshot & normalization --------------------------------------------------


def strip_meta_fields(obj Any) - Any
    Remove noisy  environment-specific fields from a GTM object.
    remove_keys = {
        path,
        tagManagerUrl,
        fingerprint,
        accountId,
        containerId,
        workspaceId,
        parentFolderId,
    }

    if isinstance(obj, dict)
        return {
            k strip_meta_fields(v)
            for k, v in obj.items()
            if k not in remove_keys
        }
    if isinstance(obj, list)
        return [strip_meta_fields(v) for v in obj]
    return obj


def build_entity_map(items List[Dict[str, Any]]) - Dict[str, Dict[str, Any]]
    
    Build a map of entity_name - normalized entity dict.

    Falls back to ID if name is missing.
    
    out Dict[str, Dict[str, Any]] = {}
    for item in items
        name = (
            item.get(name)
            or item.get(tagId)
            or item.get(triggerId)
            or item.get(variableId)
        )
        if not name
            # skip unnamed items to keep things sane
            continue
        out[name] = strip_meta_fields(item)
    return out


def snapshot_container(service, account_name str, container_name str) - Dict[str, Any]
    
    Fetch a 'snapshot' of a container's tags, triggers, and variables
    from its default workspace.
    
    account_id = find_account_id(service, account_name)
    container = find_container(service, account_id, container_name)
    container_path = container[path]

    workspace = find_default_workspace(service, container_path)
    workspace_path = workspace[path]

    tags_result = (
        service.accounts()
        .containers()
        .workspaces()
        .tags()
        .list(parent=workspace_path)
        .execute()
    )
    triggers_result = (
        service.accounts()
        .containers()
        .workspaces()
        .triggers()
        .list(parent=workspace_path)
        .execute()
    )
    variables_result = (
        service.accounts()
        .containers()
        .workspaces()
        .variables()
        .list(parent=workspace_path)
        .execute()
    )

    tags = tags_result.get(tag, [])
    triggers = triggers_result.get(trigger, [])
    variables = variables_result.get(variable, [])

    return {
        tags build_entity_map(tags),
        triggers build_entity_map(triggers),
        variables build_entity_map(variables),
    }


# --- Diff helpers --------------------------------------------------------------


def flatten(obj Any, prefix str = ) - Dict[str, Any]
    
    Flatten nested dictlist structures into a single-level dict

        {a {b [1, 2]}}
        - {a.b[0] 1, a.b[1] 2}
    
    items Dict[str, Any] = {}

    if isinstance(obj, dict)
        for k, v in obj.items()
            new_prefix = f{prefix}.{k} if prefix else k
            items.update(flatten(v, new_prefix))
    elif isinstance(obj, list)
        for idx, v in enumerate(obj)
            new_prefix = f{prefix}[{idx}]
            items.update(flatten(v, new_prefix))
    else
        items[prefix] = obj

    return items


def diff_snapshots(
    snap_a Dict[str, Any],
    snap_b Dict[str, Any],
    label_a str = A,
    label_b str = B,
) - List[Dict[str, Any]]
    
    Compute field-level differences between two container snapshots.

    Returns a list of rows suitable for CSV export
        {
            entity_type tagtriggervariable,
            entity_name ...,
            field_path parameters[0].value,
            value_a ...,
            value_b ...,
            label_a label_a,
            label_b label_b,
            change_type only_in_aonly_in_bmodified
        }
    
    rows List[Dict[str, Any]] = []

    for entity_type in (tags, triggers, variables)
        map_a Dict[str, Any] = snap_a.get(entity_type, {})
        map_b Dict[str, Any] = snap_b.get(entity_type, {})

        names = sorted(set(map_a.keys())  set(map_b.keys()))

        for name in names
            a = map_a.get(name)
            b = map_b.get(name)

            if a is None
                rows.append(
                    {
                        entity_type entity_type,
                        entity_name name,
                        field_path __entity__,
                        value_a ,
                        value_b present,
                        label_a label_a,
                        label_b label_b,
                        change_type only_in_b,
                    }
                )
                continue

            if b is None
                rows.append(
                    {
                        entity_type entity_type,
                        entity_name name,
                        field_path __entity__,
                        value_a present,
                        value_b ,
                        label_a label_a,
                        label_b label_b,
                        change_type only_in_a,
                    }
                )
                continue

            flat_a = flatten(a)
            flat_b = flatten(b)
            field_paths = sorted(set(flat_a.keys())  set(flat_b.keys()))

            for path in field_paths
                va = flat_a.get(path)
                vb = flat_b.get(path)
                if va == vb
                    continue
                rows.append(
                    {
                        entity_type entity_type,
                        entity_name name,
                        field_path path,
                        value_a va if va is not None else ,
                        value_b vb if vb is not None else ,
                        label_a label_a,
                        label_b label_b,
                        change_type modified,
                    }
                )

    return rows


def export_internal_diffs_csv(
    snap_a Dict[str, Any],
    snap_b Dict[str, Any],
    label_a str,
    label_b str,
    filename str,
) - None
    Write snapshot differences to a CSV file.
    rows = diff_snapshots(snap_a, snap_b, label_a=label_a, label_b=label_b)
