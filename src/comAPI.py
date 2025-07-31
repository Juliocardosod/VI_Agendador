import requests

def send_teams_message(payload, url):
    try:
        # response = ""
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return "true"
        else:
            return f"[API] - Falha ao enviar mensagem. Canal: {payload.canal} Status code: {response.status_code} MSG: {response.text}"
    except Exception as ex:
        return f"[API] - {ex}"