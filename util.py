def GetTextUser(message):
    text = ""
    typeMessage = message["type"]

    if(typeMessage == "text"):
        text = (message["text"])["body"]

    elif typeMessage == "interactive":
        interactiveObject = message["interactive"]
        typeInteractive = interactiveObject["type"]
        # Verifica el tipo de mensaje interactivo
        if typeInteractive == "button_reply":
            text = (interactiveObject["button_reply"])["title"]
        elif typeInteractive == "list_reply":
            text = (interactiveObject["list_reply"])["title"]
        else:
            print("Tipo de mensaje interactivo no soportado")
    else:
        print("Sin mensaje de texto")

    return text 

# Funcioon para crear un mensaje de texto para WhatsApp
# Esta funcion recibe el texto del usuario y el numero de telefono
def TextMessage(textUser, number):
    data = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {
            "body": textUser}
    }
    return data
def TextMessage1(textUser, number):
    data = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {
            "body": "Te invitamos a reportar peligros, amenazas, incidentes, errores operacionales o cualquier otra condición que identifiques, para proteger tu seguridad, la de tus compañeros y la de la Empresa. 🚨⚡🚧⚠️"}
    }
    return data


# Función para crear un mensaje de formato de texto enriquecido para WhatsApp
# Esta función recibe el número de teléfono y crea un mensaje con diferentes formatos de texto
def TextFormatMessage(number):
    data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "body": "*Hola bienvenido!* - _Hola bienvenido!_ - ~Hola bienvenido!~ - ```Hola bienvenido!```"
            }
        }
    return data
# Función para crear un mensaje de imagen para WhatsApp
# Esta función recibe el número de teléfono y crea un mensaje que contiene una imagen
def ImageMessage(number):
    data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "image",
            "image": {
                "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/image_whatsapp.png"
            }
        }
    return data

# Funccion para crear un mensaje de audio para WhatsApp
# Esta función recibe el número de teléfono y crea un mensaje que contiene un archivo de audio
def AudioMessage(number):
    data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "audio",
            "audio": {
                "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/audio_whatsapp.mp3"
            }
        }
    return data

# Función para crear un mensaje de video para WhatsApp
# Esta función recibe el número de teléfono y crea un mensaje que contiene un archivo de video
def VideoMessage(number):
    data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "video",
            "video": {
                "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/video_whatsapp.mp4"
            }
        }
    return data

def LocationMessage(number):
    data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "location",
            "location": {
            "latitude":"5.04954898906084",
            "longitude":"-75.53159544273188",
            "name":"CHEC Estación uribe",
            "address":"EL TABLAZO, Manizales, Villamaría, Caldas"
            }
        }
    return data

# Función para crear un mensaje de documento para WhatsApp
# Esta función recibe el número de teléfono y crea un mensaje que contiene un archivo de documento
def DocumentMessage(number):
    data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/document_whatsapp.pdf"
            }
        }
    return data

# Función para crear un mensaje de botones interactivos para WhatsApp
# Esta función recibe el número de teléfono y crea un mensaje que contiene botones interactivos
def ButtonsMessage(number):
    data ={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Confirmas tu registro?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "001",
                                "title": "✅ SI"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "002",
                                "title": "❌ NO"
                            }
                        }
                    ]
                }
            }
        }
    return data

# Función para crear un mensaje de lista interactiva para WhatsApp
# Esta función recibe el número de teléfono y crea un mensaje que contiene una lista de opciones inter
def ListTipo(number):
    data = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "✅ ¿La novedad que vas a reportar, te afecta a ti, a una persona o a varias personas?."
            },
            "footer": {
                "text": "Seleccione una opción"
            },
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Opciones de reporte",
                        "rows": [
                            {
                                "id": "1",
                                "title": "Me afecta"
                            },
                            {
                                "id": "2",
                                "title": "Afecta a una persona"                                
                            },
                            {
                                "id": "3",
                                "title": "Afecta a varias personas"                                
                            }
                        ]
                    }
                ]
            }
        }
    }
    return data

def ListTiempo(number):
    data = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "📆 ¿Cuándo ocurrió la Novedad?. Por favor, elija una opción"
            },
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Opciones de reporte",
                        "rows": [
                            {
                                "id": "1",
                                "title": "Hoy"
                            },
                            {
                                "id": "2",
                                "title": "Ayer"                                
                            },
                            {
                                "id": "3",
                                "title": "Antier"                                
                            },
                            {
                                "id": "4",
                                "title": "Otra Fecha"                                
                            }
                        ]
                    }
                ]
            }
        }
    }
    return data

def ListSeguridad(number):
    data = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "✅ Selecciona la opción que describa mejor la novedad que vas a reportar."
            },
            "footer": {
                "text": "Seleccione una opción"
            },
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Opciones de reporte",
                        "rows": [
                            {
                                "id": "1",
                                "title": "Seguridad en personas"
                            },
                            {
                                "id": "2",
                                "title": "Seguridad en activos"                                
                            }
                        ]
                    }
                ]
            }
        }
    }
    return data


def Buttonsningunapersona(number):
    data ={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "✅ ¿Deseas volver a buscar, o ingresar los datos manualmente?. Elige una opción"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "001",
                                "title": "Si volver a buscar"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "002",
                                "title": "Ingresar manualmente"
                            }
                        }
                    ]
                }
            }
        }
    return data

def ButtonsValTranscr(number):
    data ={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "✅ ¿Estás de acuerdo con esta transcripción?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "1",
                                "title": "Estoy de acuerdo" # MAXIMO 20 CARACTERES
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "2",
                                "title": "Volver a enviarla" # MAXIMO 20 CARACTERES
                            }
                        }
                    ]
                }
            }
        }
    return data


def ButtonsTienesFotos(number):
    data ={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "📸 Tienes fotos o videos?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "1",
                                "title": "Si tengo" # MAXIMO 20 CARACTERES
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "2",
                                "title": "No tengo" # MAXIMO 20 CARACTERES
                            }
                        }
                    ]
                }
            }
        }
    return data




# def ListMessage(number):
#     data = {
#             "messaging_product": "whatsapp",
#             "to": number,
#             "type": "interactive",
#             "interactive": {
#                 "type": "list",
#                 "body": {
#                     "text": "✅ Tenemos estas opciones"
#                 },
#                 "footer": {
#                     "text": "Seleccione una opción"
#                 },
#                 "action": {
#                     "button": "See options",
#                     "sections": [
#                         {
#                             "title": "Buy and sell products",
#                             "rows": [
#                                 {
#                                     "id": "main-buy",
#                                     "title": "Buy",
#                                     "description": "Buy the best product your home"
#                                 },
#                                 {
#                                     "id": "main-sell",
#                                     "title": "Sell",
#                                     "description": "Sell your products"
#                                 }
#                             ]
#                         },
#                         {
#                             "title": "📍center of attention",
#                             "rows": [
#                                 {
#                                     "id": "main-agency",
#                                     "title": "Agency",
#                                     "description": "Your can visit our agency"
#                                 },
#                                 {
#                                     "id": "main-contact",
#                                     "title": "Contact center",
#                                     "description": "One of our agents will assist you"
#                                 }
#                             ]
#                         }
#                     ]
#                 }
#             }
#         }
#     return data