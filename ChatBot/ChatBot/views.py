from django.shortcuts import redirect, render
import openai, os
from dotenv import load_dotenv
from django.contrib.sessions.models import Session
import uuid

load_dotenv()

api_key = os.getenv('OPENAI_KEY', None)

openai.api_key = api_key

def chatbot(request):
    eliminar_sesiones(request)
    return render(request, 'main.html', {})


def panel(request):
    if request.method == 'GET' and 'user_input' in request.GET:
        tema = request.GET.get('user_input')
        request.session['tema'] = tema
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Actúa como profesor para alumnos de 10 años. Responde claro y conciso en 3 párrafos + 3 conceptos clave + posibles ejemplos/analogías sobre {tema}. Pregunta si hay más dudas."
                },
            ],
            temperature=0.9,
        )
        contenido = response.choices[0].message.content
        response_data = request.session.get('response_data', [])
        response_data.append({'id': str(uuid.uuid4()), 'tipo': 'tema', 'contenido': contenido})
        request.session['response_data'] = response_data
    else:
        tema = request.session.get('tema', None)
        response_data = request.session.get('response_data', None)
    
    return render(request, 'panel.html', {'tema': tema, 'response_data': response_data})

def tema(request):
    response_data = request.session.get('response_data', [])
    for i in response_data:
        if i['tipo'] == 'tema':
            contenido_tema = i['contenido']
            break
    return render(request, 'panel.html', {'tema': tema, 'contenido_tema': contenido_tema, 'response_data': response_data})

def ejemplos(request):
    tema = request.session.get('tema', None)
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Actúa como profesor para alumnos de 10 años. Tema: {tema}. Provee 5 ejemplos relacionados. Responde directamente sin saludar."
                },
            ],
            temperature=0.9,
        )
    contenido = response.choices[0].message.content
    response_data = request.session.get('response_data', [])
    response_data.append({'id': str(uuid.uuid4()), 'tipo': 'ejemplo', 'contenido': contenido})
    request.session['response_data'] = response_data
    return redirect('panel')

def adicional(request):
    tema = request.session.get('tema', None)
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Actúa como profesor para alumnos de 10 años. Tema: {tema}. Proporciona 5 hipervínculos de contenido en español relacionados para su edad. Responde directamente sin saludar."
                },
            ],
            temperature=0.9,
        )
    contenido = response.choices[0].message.content
    response_data = request.session.get('response_data', [])
    response_data.append({'id': str(uuid.uuid4()), 'tipo': 'adicional', 'contenido': contenido})
    request.session['response_data'] = response_data
    return redirect('panel')

def ejercicior(request):
    tema = request.session.get('tema', None)
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Actúa como profesor para alumnos de 10 años. Tema: {tema}. Plantea un ejercicio relacionado que se resuelva en cinco minutos. Luego, resuelve el ejercicio paso a paso con razonamientos. No repitas ejercicios."
                },
            ],
            temperature=0.9,
        )
    contenido = response.choices[0].message.content
    response_data = request.session.get('response_data', [])
    response_data.append({'id': str(uuid.uuid4()), 'tipo': 'ejercicio_resuelto', 'contenido': contenido})
    request.session['response_data'] = response_data
    return redirect('panel')

def ejercicio(request):
    tema = request.session.get('tema', None)
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Actúa como profesor para alumnos de 10 años. Tema: {tema}. Plantea un ejercicio relacionado que se resuelva en cinco minutos y espera la respuesta del alumno. Si responde incorrectamente, puedes brindar pistas para ayudar, pero no des la respuesta correcta incluso si la solicita. Si la respuesta es correcta, felicítalo."
                },
            ],
            temperature=0.9,
        )
    contenido = response.choices[0].message.content
    response_data = request.session.get('response_data', [])
    response_data.append({'id': str(uuid.uuid4()), 'tipo': 'ejercicio', 'contenido': contenido})
    request.session['response_data'] = response_data
    return redirect('panel')

def pregunta(request):
    if request.method == 'POST':
        tema = request.session.get('tema', None)
        pregunta = request.POST.get('user_respuesta')
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Actúa como profesor para alumnos de 10 años. Tema: {tema}. Responde la pregunta sin saludar en un párrafo simple y solo si está relacionada al tema. Si no, indica que no puedes responder."
                    },
                    {
                        "role": "user",
                        "content": pregunta
                    }
                ],
                temperature=0.9,
            )
        contenido = response.choices[0].message.content
        response_data = request.session.get('response_data', [])
        response_data.append({'id': str(uuid.uuid4()), 'tipo': 'pregunta', 'contenido': contenido, 'pregunta': pregunta}) 
        request.session['response_data'] = response_data
        return redirect('panel')

def eliminar_sesiones(request):
    Session.objects.all().delete()