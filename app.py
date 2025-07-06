from flask import Flask, render_template, request
from openai import OpenAI
import pdfplumber
import os
from dotenv import load_dotenv
load_dotenv()

# Sua chave da OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

def extrair_texto_arquivo(arquivo):
    if arquivo.filename.endswith('.pdf'):
        with pdfplumber.open(arquivo) as pdf:
            texto = ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])
        return texto
    elif arquivo.filename.endswith('.txt'):
        return arquivo.read().decode('utf-8')
    return ''

def classificar_email(email_texto):
    prompt_classificacao = f"""
    Classifique o seguinte email como PRODUTIVO ou IMPRODUTIVO:

    "{email_texto}"

    Responda apenas com: PRODUTIVO ou IMPRODUTIVO.
    """

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_classificacao}]
    )
    categoria = resposta.choices[0].message.content.strip().upper()

    if categoria not in ['PRODUTIVO', 'IMPRODUTIVO']:
        categoria = "INDEFINIDO"

    return categoria

def gerar_resposta(email_texto, categoria):
    prompt_resposta = f"""
    Email recebido:
    "{email_texto}"

    Categoria: {categoria}

    Gere uma resposta automática apropriada para esse email.
    """

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_resposta}]
    )
    return resposta.choices[0].message.content.strip()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    texto_email = request.form.get('email_texto')

    if not texto_email and 'email_arquivo' in request.files:
        arquivo = request.files['email_arquivo']
        texto_email = extrair_texto_arquivo(arquivo)

    if not texto_email:
        return render_template('index.html', resultado={'categoria': 'Erro', 'resposta': 'Nenhum texto encontrado!'})

    categoria = classificar_email(texto_email)
    resposta = gerar_resposta(texto_email, categoria)

    resultado = {
        'categoria': categoria,
        'resposta': resposta
    }

    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
