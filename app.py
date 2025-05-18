import os
import textwrap
import requests
import warnings
import json
import re

from flask import Flask, render_template, request, redirect, url_for, session
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from werkzeug.utils import secure_filename  # Para segurança no upload
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_KEY')  # Chave para sessões (mantenha seguro em produção)
UPLOAD_FOLDER = 'uploads'  # Pasta para salvar os arquivos enviados
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Cria a pasta se não existir

# Sua chave da API do Gemini (substitua pelo método seguro em produção)
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')

# Função auxiliar para chamar o agente (igual ao notebook)
def call_agent(agent: Agent, message_text: str, arquivo_pdf=None) -> str:
    """
    Chama um agente com uma mensagem e, opcionalmente, um arquivo PDF.

    Args:
        agent: O agente a ser chamado.
        message_text: O texto da mensagem para o agente.
        arquivo_pdf: O conteúdo do arquivo PDF (se houver).

    Returns:
        A resposta do agente como uma string.
    """
    session_service = InMemorySessionService()
    session_id = session.get('session_id', 'session1')  # Pega o ID da sessão ou usa um padrão
    session_obj = session_service.create_session(app_name=agent.name, user_id="user1", session_id=session_id)
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)

    if arquivo_pdf:
        artifact = types.Part(
            inline_data=types.Blob(data=arquivo_pdf, mime_type="application/pdf")
        )
        content = types.Content(role="user", parts=[types.Part(text=message_text), artifact])
    else:
        content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="user1", session_id=session_id, new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text + "\n"

    session['session_id'] = session_id  # Atualiza o ID da sessão
    return final_response

# Agentes (igual ao notebook)
def agente_arquiteto_trilha(area_formacao, formacao_previa, area_enfase, lista_objetivos, orcamento, tempo):
    """
    Agente que gera trilhas de estudo personalizadas.

    Args:
        area_formacao: A área de formação do usuário.
        formacao_previa: O currículo/experiência prévia do usuário (opcional).
        area_enfase: A área de ênfase desejada na trilha (opcional).
        lista_objetivos: Uma lista de objetivos de aprendizado (opcional).
        orcamento: O orçamento do usuário.
        tempo: O tempo disponível do usuário.

    Returns:
        A trilha de estudo gerada como uma string.
    """
    instruction = """
      Você é um gerador de trilhas de formação para profissionais. A sua tarefa é usar a ferramenta de busca do 
      google (google_search) para recuperar os conhecimentos necessários para um profissional atuar em sua área 
      de formação.
      A trilha necessita ser atualizada e sólida, garantindo que ela tenha os conhecimentos necessários, 
      relevantes e atuais para atuar na área de formação informada.
      Caso receba Área de enfâse da trilha, Objetivos da trilha e/ou Formação prévia. A trilha deve se basear
      totalmente neles. Garantindo que os objetivos e a ênfase devem ser alcançados e que a trilha não possua
      conhecimentos que já foram estudados na formação prévia.
      O retorno deve ser apenas a trilha deve com conhecimentos, tempo, e ferramentas necessários. NÃO deve possuir 
      cursos, recursos, plataformas, detalhes.
      O formato da sua resposta deve ser um JSON formatado na forma a seguir:
      {
        [
          {
            "materia": {
              "titulo": "titulo da materia",
              "disciplinas": [{"titulo":"displina1"}, {{"titulo":"displina2"}...]
            },
            "tempo": "2 meses",
          },
          {
            "materia": {
              "titulo": "titulo da materia",
              "disciplinas": [{"titulo":"displina1"}, {{"titulo":"displina2"}...]
            },
            "tempo": "2 meses",
          },
        ]
      }
      """
    if formacao_previa:
        instruction += """
        Leve em conta o currículo com a experiência prévia em anexo para não recomendar
        cursos já realizados ou conhecimentos já adquiridos pela pessoa.
        """
    if lista_objetivos:
        instruction += f"\n Certifique-se que quem estudar a trilha seja capaz de: {', '.join(lista_objetivos)}"

    arquiteto = Agent(
        name="agente_arquiteto_trilha",
        model="gemini-2.0-flash",
        instruction=instruction,
        description="Agente que busca informações de uma formação no Google e gera uma trilha de estudos",
        tools=[google_search]
    )

    entrada_do_agente_arquiteto_trilha = f"Área de formação: {area_formacao}\n Orçamento: {orcamento}\n Tempo: {tempo}"
    if area_enfase:
        entrada_do_agente_arquiteto_trilha += f"\n Área de enfâse da trilha: {area_enfase}"

    lancamentos = call_agent(arquiteto, entrada_do_agente_arquiteto_trilha, arquivo_pdf=formacao_previa)
    return lancamentos

def agente_curador_cursos(trilha, orcamento, tempo):
    """
    Agente que curadoria cursos online relevantes para uma trilha de estudo.

    Args:
        trilha: A trilha de estudo gerada.
        orcamento: O orçamento do usuário.
        tempo: O tempo disponível do usuário.

    Returns:
        A trilha de estudo com cursos recomendados como uma string.
    """
    instruction = """
      Você é um curador de cursos, especialista em recomendar cursos onlines. Com base na trilha 
      de estudo, tempo e orçamento recebidos, no formato a seguir, você deve:
      {
        [
          {
            "materia": {
              "titulo": "titulo da materia",
              "disciplinas": [{"titulo":"displina1"}, {{"titulo":"displina2"}...]
            },
            "tempo": "2 meses",
          },
          {
            "materia": {
              "titulo": "titulo da materia",
              "disciplinas": [{"titulo":"displina1"}, {{"titulo":"displina2"}...]
            },
            "tempo": "2 meses",
          },
        ]
      }
      Usar a ferramenta de busca do Google (google_search) para achar cursos de instituições 
      seguras que se adequam aos conhecimentos presentes na trilha de estudo.
      Você deve recomendar ao total dois cursos online por matéria.
      Você deve adicionar dentro de cada chave de matéria, cinco chaves de cursos(com campo titulo, 
      link e preço do curso). Ex: "curso": {"titulo":"tit...","link":http:..., "preco":"500"}.
      Você deve retornar apenas o json e NÃO deve retirar informações do arquivo json.
      Certifique-se que todos os cursos possuem links e domínios existentes ao clicar.
      Certifique-se que o custo total dos cursos e o tempo total de estudo devem ser abaixo do 
      tempo e orçamento informados e que os cursos não sejam de pagamento 
      por assinatura. Recomende apenas cursos que atendam a esses critérios.
      """
    curador_cursos = Agent(
        name="agente_curador_cursos",
        model="gemini-2.0-flash",
        instruction=instruction,
        description="Agente que realiza curadoria e recomenda cursos",
        tools=[google_search]
    )

    entrada_do_agente_curador_cursos = f"Trilha:{trilha}\n Orçamento: {orcamento} \n Tempo: {tempo}"

    trilha_com_cursos = call_agent(curador_cursos, entrada_do_agente_curador_cursos, None)
    return trilha_com_cursos

def agente_criador_notion(materia):
    """
    Agente que cria templates de anotações para o Notion.

    Args:
        materia: A matéria/tópico para o qual criar o template.

    Returns:
        O template do Notion como uma string.
    """
    instruction = """
          Você é um Criador de Templates do Notion meticuloso, especializado em receber matérias 
          com disciplinas e cursos para criar um JSON de template para o notion.
          A matéria é uma lista com diversos dicionários. Cada dicionário possui uma matéria,
          com título, tempo e lista de disciplinas.
          Utilize esse JSON para criar JSON de criação de template para a Notion API. A formatação final
          terá que ser de acordo com o exemplo a seguir:
          {
            "properties": {
              "title": {
                "id": "title",
                "type": "title",
                "title": [
                  {
                    "type": "text",
                    "text": {
                      "content": "Área 1",
                      "link": None
                    },
                    "annotations": {
                      "bold": False,
                      "italic": False,
                      "strikethrough": False,
                      "underline": False,
                      "code": False,
                      "color": "default"
                    },
                    "plain_text": "This is also not done",
                    "href": None
                  }
                ]
              }
            },
            "children": [
              {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                  "rich_text": [{ "type": "text", "text": { "content": "Cursos Recomendados:" } }]
                }
              },
              {
                "object": "block",
                "type": "table",
                "table": {
                  "table_width": 4,
                  "children":[{
                        "type": "table_row",
                        "table_row": {
                          "cells":[
                            [{
                              "type": "text",
                              "text": {
                                "content": 'Nome do Curso',
                              }
                            }],
                            [{
                              "type": "text",
                              "text": {
                                "content": 'Duração',
                              }
                            }],
                            [{
                              "type": "text",
                              "text": {
                                "content": 'Investimento',
                              }
                            }],
                            [{
                              "type": "text",
                              "text": {
                                "content": 'Página do Curso',
                              }
                            }]
                          ]
                        }
                      },
                      {
                      "type": "table_row",
                      "table_row": {
                        "cells":[
                          [{
                            "type": "text",
                            "text": {
                              "content": 'Curso 1',
                            }
                          }],
                          [{
                            "type": "text",
                            "text": {
                              "content": '18:00h',
                            }
                          }],
                          [{
                            "type": "text",
                            "text": {
                              "content": '20,00R$',
                            }
                          }],
                          [{
                            "type": "text",
                            "text": {
                              "content": 'https://www.teste.com.br',
                            }
                          }]
                        ]
                      }
                  }]
                }
              },
              {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                  "rich_text": [{ "type": "text", "text": { "content": "Checklist - Curso 1" } }]
                }
              },
              {
                "object": "block",
                "type": "to_do",
                "to_do": {
                  "rich_text": [{
                    "type": "text",
                    "text": {
                      "content": "Módulo 1",
                      "link": None
                    }
                  }],
                  "checked": False,
                  "color": "default"
                }
              },
              {
                "object": "block",
                "type": "to_do",
                "to_do": {
                  "rich_text": [{
                    "type": "text",
                    "text": {
                      "content": "Módulo 2",
                      "link": None
                    }
                  }],
                  "checked": False,
                  "color": "default"
                }
              },
              {
                "object": "block",
                "type": "to_do",
                "to_do": {
                  "rich_text": [{
                    "type": "text",
                    "text": {
                      "content": "Módulo 3",
                      "link": None
                    }
                  }],
                  "checked": False,
                  "color": "default"
                }
              }
            ]
          }
          Alterando 'Área 1' pelo nome da matéria, 'Curso x' pelo nome do
          respectivo curso da matéria, '18:00h' pelo tempo do respectivo curso, 
          '20,00R$' pelo preço do respectivo curso, 'https://www.teste.com.br' 
          pelo link do respectivo curso, 'Checklist - Curso x' para Checklist -
          nome respectivo curso e 'Módulo 1', 'Módulo 2', 'Módulo 3', para o
          nome das disciplinas da matéria.
          Gere o retorno do JSON em formato byte.
          """
    criador = Agent(
        name="agente_criador_notion",
        model="gemini-2.0-flash",
        instruction=instruction,
        description="Agente criador de templates para o Notion"
    )
    entrada_do_agente_criador = f"Matéria: {materia}"

    template = call_agent(criador, entrada_do_agente_criador)
    return template

def markdown_to_json(trilha):
    """
    Converte uma string Markdown contendo um bloco de código JSON em um objeto JSON.

    Args:
        trilha: A string Markdown a ser convertida.

    Returns:
        Um objeto JSON ou None em caso de erro.
    """
    json_match = re.search(r'`json\n(.*?)\n`', trilha, re.DOTALL)

    if json_match:
        json_string = json_match.group(1)
        try:
            retorno = json.loads(json_string)
            print("JSON decodificado com sucesso!")
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON após extração: {e}")
            print(f"String JSON extraída:\n'{json_string}'")
            return None  # Retorna None em caso de erro de decodificação
    else:
        print("Bloco de código JSON não encontrado na saída Markdown.")
        return None  # Retorna None se nenhum bloco JSON for encontrado

    return retorno

# Rotas do Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Rota para a página inicial do aplicativo.
    Permite ao usuário inserir seus dados para gerar uma trilha de estudos.
    """
    if request.method == 'POST':
        session.clear()  # Limpa a sessão anterior
        session['area_formacao'] = request.form['area_formacao']
        session['orcamento'] = request.form['orcamento']
        session['tempo'] = request.form['tempo']
        session['area_enfase'] = request.form.get('area_enfase', None)
        session['lista_objetivos'] = [obj for obj in request.form.getlist('objetivo') if obj]

        # Lógica para formação prévia (upload de arquivo)
        formacao_previa = None
        if 'formacao_previa' in request.files:
            file = request.files['formacao_previa']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                with open(filepath, "rb") as f:
                    formacao_previa = f.read()
                session['formacao_previa_filename'] = filename  # Salva o nome do arquivo para referência futura

        trilha_estudo = agente_arquiteto_trilha(
            session['area_formacao'], formacao_previa, session['area_enfase'],
            session['lista_objetivos'], session['orcamento'], session['tempo']
        )
        session['trilha_estudo'] = trilha_estudo
        return redirect(url_for('cursos'))
    return render_template('index.html')

@app.route('/cursos')
def cursos():
    """
    Rota para a página de cursos recomendados.
    Exibe os cursos recomendados com base na trilha de estudos gerada.
    """
    print(session)
    trilha_estudo = session.get('trilha_estudo')
    if not trilha_estudo:
        return redirect(url_for('index'))

    trilha_estudo_com_cursos = agente_curador_cursos(trilha_estudo, session['orcamento'], session['tempo'])
    session['trilha_estudo_com_cursos'] = markdown_to_json(trilha_estudo_com_cursos)
    return render_template('cursos.html', trilha_estudo_com_cursos=session['trilha_estudo_com_cursos'])

@app.route('/notion')
def notion():
    """
    Rota para a página de templates do Notion.
    Gera e exibe templates do Notion para cada matéria na trilha de estudos.
    """
    trilha_estudo_com_cursos = session.get('trilha_estudo_com_cursos')
    if not trilha_estudo_com_cursos:
        return redirect(url_for('index'))

    lista_materias = []
    for materia in trilha_estudo_com_cursos:
        template_notion = agente_criador_notion(materia)
        lista_materias.append(markdown_to_json(template_notion))

    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    PAGE_ID = os.getenv('PAGE_ID')
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    url = 'https://api.notion.com/v1/pages'

    for materia in lista_materias:
        payload = {
            "parent": { "page_id": PAGE_ID },
        "icon": {
            "emoji": "📖"
        },
            "cover": {
                "external": {
                    "url": "https://images.pexels.com/photos/1106468/pexels-photo-1106468.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
                }
            },
        "properties": materia.get('properties'),
        "children": materia.get('children')
        }
        response = requests.post(url, json=payload, headers=headers)

    return render_template('notion.html', page_id=PAGE_ID)

if __name__ == '__main__':
    app.run(debug=True)
