"""Funcoes de acesso a API do Instagram (Graph API) para publicar carrosseis."""
import time

import requests

GRAPH = "https://graph.facebook.com/v21.0"


def clean_secret(value):
    """Remove espacos, quebras de linha e caracteres nao imprimiveis que a colagem possa ter trazido."""
    return "".join(ch for ch in (value or "") if ch.isprintable() and not ch.isspace())


def graph_post(path, **params):
    r = requests.post(f"{GRAPH}/{path}", data=params, timeout=60)
    body = r.json()
    if r.status_code >= 400:
        raise RuntimeError(f"Graph API {path}: {body.get('error', body)}")
    return body


def graph_get(path, **params):
    r = requests.get(f"{GRAPH}/{path}", params=params, timeout=60)
    body = r.json()
    if r.status_code >= 400:
        raise RuntimeError(f"Graph API {path}: {body.get('error', body)}")
    return body


def resolve_ig(user_id, token):
    """Aceita token de Pagina ou de usuario; descobre a conta do Instagram pelo token quando o ID nao e informado."""
    if user_id.isdigit():
        r = requests.get(f"{GRAPH}/{user_id}", params={"fields": "id", "access_token": token}, timeout=60)
        if r.status_code == 200:
            return user_id, token
    r = requests.get(
        f"{GRAPH}/me/accounts",
        params={"fields": "name,access_token,instagram_business_account", "access_token": token},
        timeout=60,
    )
    pages = [p for p in r.json().get("data", []) if p.get("instagram_business_account")] if r.status_code < 400 else []
    if not pages:
        me = requests.get(f"{GRAPH}/me", params={"fields": "id,name,instagram_business_account", "access_token": token}, timeout=60)
        mb = me.json()
        if me.status_code < 400 and mb.get("instagram_business_account"):
            return mb["instagram_business_account"]["id"], token
        raise RuntimeError("Nenhuma Pagina com Instagram vinculado foi encontrada para este token")
    page = pages[0]
    return page["instagram_business_account"]["id"], page["access_token"]


def wait_public(url, tries=12):
    for _ in range(tries):
        if requests.head(url, timeout=30).status_code == 200:
            return
        time.sleep(10)
    raise RuntimeError(f"Imagem nao acessivel publicamente: {url}")


def wait_finished(container, token, tries=40):
    for _ in range(tries):
        status = graph_get(container, fields="status_code", access_token=token)["status_code"]
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {container} com status {status}")
        time.sleep(5)
    raise RuntimeError(f"Container {container} nao ficou pronto a tempo")


def publish_carousel(user_id, token, image_urls, caption):
    """Cria um container por imagem, o container do carrossel e publica. Retorna o media_id."""
    for u in image_urls:
        wait_public(u)
    children = []
    for u in image_urls:
        cid = graph_post(f"{user_id}/media", image_url=u, is_carousel_item="true", access_token=token)["id"]
        wait_finished(cid, token)
        children.append(cid)
    parent = graph_post(
        f"{user_id}/media",
        media_type="CAROUSEL",
        children=",".join(children),
        caption=caption,
        access_token=token,
    )["id"]
    wait_finished(parent, token)
    return graph_post(f"{user_id}/media_publish", creation_id=parent, access_token=token)["id"]
