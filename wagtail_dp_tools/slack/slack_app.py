import os
import threading
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from django.conf import settings
from django.apps import apps
from wagtail_dp_tools.slack.slack_actions import generate_response, getUser, validate_authorization

slack_app_token = settings.SLACK['SLACK_APP_TOKEN']
slack_bot_token = settings.SLACK['SLACK_BOT_TOKEN']

app = App(token=slack_bot_token)
print('app:: ', app)

# Cargamos datos dummies
# apps = {
#     "cacheClear": {
#         "name": "Borrar cache",
#         "description": "El usuario desea borrar el cache de la aplicación",
#         "Confirm": "¿Está seguro de que desea borrar el cache de la aplicación?",
#         "success": "El cache de la aplicación ha sido borrado",
#         "problem": "El cache de la aplicación no ha podido ser borrado",
#         "services": []
#     },
# }

@app.event("app_mention")
def handle_message(event, say):
    user = event.get("user")
    text = event.get("text")
    channel = event.get("channel")
    message_ts = event.get("ts")
    evenData = event
    user_id = event.get("user")

    name, mail = getUser(user_id, app)
    is_authorized = validate_authorization(user_id)

    if not is_authorized:
        say(
            text=f"<@{user}> No tienes autorización para realizar esta acción.",
            thread_ts=message_ts
        )
        return

    # print(f"Mensaje recibido de {user} en {channel}: {text}")
    print('evenData: ', evenData)
    print('==============================')
    print(f"Mensaje recibido de {name} ({mail}): {text}")

    text_no_mention = text.replace(f"<@{user}>", "").strip()
    ia_response = generate_response(text_no_mention)

    # Responder al canal
    say(
        text= f"<@{user}> {ia_response}",
        thread_ts= message_ts
    )

def start_socket_mode():
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()
  
# Ejecutar Socket Mode en un hilo aparte para no bloquear Django
def run_async():
    thread = threading.Thread(target=start_socket_mode, daemon=True)
    thread.start()
