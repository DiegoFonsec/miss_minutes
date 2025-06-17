import openai 
from django.conf import settings
from slack_sdk.errors import SlackApiError

openai.api_key = settings.OPEN_IA['API_KEY']

def generate_response(user_text):
    """
    Generate a response from OpenAI's GPT-3.5 Turbo model based on the user's input.
    """
    try:
        response = openai.ChatCompletion.create(
            model="o3-mini",
            messages=[
                {"role": "user", "content": user_text}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Lo siento, no pude generar una respuesta en este momento."

def getUser(user_id, app):
    try:
        response = app.client.users_info(user=user_id)
        user = response['user']
        nombre = user.get('real_name', "nombre no disponible")
        email = user.get('profile', {}).get('email', "email no disponible")
        return nombre, email
    except SlackApiError as e:
        print(f"Error al obtener información del usuario: {e.response['error']}")
        return "desconocido", "desconocido"

def validate_authorization(user_id):
    """
    Validate if the user is authorized to perform actions.
    This is a placeholder function; implement your own logic as needed.
    """
    # For now, we assume all users are authorized
    return True