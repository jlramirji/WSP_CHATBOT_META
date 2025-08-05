import requests
import json

def SendMessageWhatsApp(data):
    try:
        #print("1. Enviando mensaje a WhatsApp")
        token="EAAU6sySSA20BO8ZA4ZAW4TiBnQcXXvxZCtprZB3ZApdSJI4u2YBg9GF9ZBvKX3n3JcSvLK2LWfD24G8QZAn4sZB2yBGP1UlbMkWz1ZBEv1wkTClF0VwZA7NpdioFB9OZBO0sgpYDmdGy6qDATAi0yeC9aTnKBlKrZCR9i18QoX5ydt7VYVsKnGdG9SXlpZCzr2G7ZBehp2jAZDZD"
        #print("2. Preparando datos para enviar el mensaje")
        api_url = "https://graph.facebook.com/v22.0/662597943605166/messages"
        #print("3. Enviando mensaje a la API de WhatsApp")
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
        #print("4. Realizando la solicitud POST")
        # data = {
        #     "messaging_product": "whatsapp",
        #     "to": number,
        #     "type": "text",
        #     "text": {"body": textUser}
        # }
        #print("5. Procesando la respuesta de la API")
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            #print("Message sent successfully")
           # print(response.json())
            return True
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"Ocurrio un error mientras se enviaba el mensaje: {e}")
        return False