# import requests
# import json
# import time

# # def enviar_mensaje_whatsapp(numero, texto):
# #     url = "http://127.0.0.1:5000/whatsapp"
# #     payload = {
# #         "object": "whatsapp_business_account",
# #         "entry": [
# #             {
# #                 "id": "3232742576873981",
# #                 "changes": [
# #                     {
# #                         "value": {
# #                             "messaging_product": "whatsapp",
# #                             "metadata": {
# #                                 "display_phone_number": None,
# #                                 "phone_number_id": "662597943605166"
# #                             },
# #                             "contacts": [
# #                                 {
# #                                     "profile": {
# #                                         "name": "User Name"
# #                                     },
# #                                     "wa_id": numero
# #                                 }
# #                             ],
# #                             "messages": [
# #                                 {
# #                                     "from": numero,
# #                                     "id": "wamid.TESTID",
# #                                     "timestamp": str(int(time.time())),
# #                                     "type": "text",
# #                                     "text": {
# #                                         "body": texto
# #                                     }
# #                                 }
# #                             ]
# #                         },
# #                         "field": "messages"
# #                     }
# #                 ]
# #             }
# #         ]
# #     }
# #     headers = {'Content-Type': 'application/json'}
# #     response = requests.post(url, headers=headers, data=json.dumps(payload))
# #     print("Respuesta:", response.text)

# # # # Ejemplo de uso:
# # #enviar_mensaje_whatsapp("573137182944", "Hola")
# # # enviar_mensaje_whatsapp("573137182944", "me afecta")
# # # enviar_mensaje_whatsapp("573137182944", "Manizales")

# def enviar_mensaje_whatsapp(numero, texto):
#     url = "http://127.0.0.1:5000/whatsapp"

#     payload = json.dumps({
#     "object": "whatsapp_business_account",
#     "entry": [
#         {
#         "id": "3232742576873981",
#         "changes": [
#             {
#             "value": {
#                 "messaging_product": "whatsapp",
#                 "metadata": {
#                 "display_phone_number": None,
#                 "phone_number_id": "662597943605166"
#                 },
#                 "contacts": [
#                 {
#                     "profile": {
#                     "name": "User Name"
#                     },
#                     "wa_id": numero
#                 }
#                 ],
#                 "messages": [
#                 {
#                     "from": numero,
#                     "id": "wamid.HBgLNTE5NDM2NjI5NjQVAAPOOQUNCODUzN0U1QkU5MkZENTFBQwA=",
#                     "timestamp": "1660362642",
#                     "type": "text",
#                     "text": {
#                     "body": texto
#                     }
#                 }
#                 ]
#             },
#             "field": "messages"
#             }
#         ]
#         }
#     ]
#     })
#     headers = {
#     'Content-Type': 'application/json'
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)

#     print(response.text)