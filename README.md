# 🧠 TrilhAI – Conectando Google AI ao Notion

### Para rodar o projeto, deve ser gerado um ambiente virtual Python (venv) - https://docs.python.org/3/library/venv.html#module-venv

# Pacotes necessários: 
```
pip install dotenv flask google-genai google-adk
```
# Comando para rodar aplicação Flask:
```
flask run
```

# É necessário chave de API do Google AI Studio e de uma Page ID e um Token de Integração do Notion. Para isso foi criado o tutorial abaixo:

## 1. Gere sua chave de API no Google AI Studio

Acesse: [https://aistudio.google.com/app/prompts/new_chat]
Clique em **"Get API Key"**.

![WhatsApp Image 2025-05-17 at 23 34 41](https://github.com/user-attachments/assets/ef2ba723-a81c-4218-9613-a4175fdb11f4)

Cole a chave de API do Google AI aqui:

---

## 2. Crie sua conta no Notion

Acesse: [https://www.notion.com/pt]

Faça login ou crie uma conta.

Crie um novo workspace para a sua conta:
- Clique no dropdown no canto superior direito da tela
- Depois clique nos três pontinhos ao lado do seu e-mail
- Clique em **Criar novo workspace**

<img src="https://github.com/user-attachments/assets/99babc33-29ed-457d-b0b9-3456535f00ff" width="300">

<img src="https://github.com/user-attachments/assets/af1e72d2-b049-4d1d-851a-2584e1bbf669" width="300">

<img src="https://github.com/user-attachments/assets/6ef6c606-90f7-400d-ab1c-3686d5824d5c" width="300">


---

## 3. Configure a integração com o Notion

Acesse o painel de integrações:  
[https://www.notion.so/profile/integrations]  
Clique em **"New Integration"**.

![WhatsApp Image 2025-05-17 at 23 34 42 (2)](https://github.com/user-attachments/assets/ba65773e-d571-436f-9c82-e10561eb90ae)

---

## 4. Nomeie e selecione o workspace

- Dê um nome para sua integração
- Selecione o workspace que você acabou de criar

Depois, vá até a aba **Configuration** e copie a **chave de integração interna**  
(`Internal Integration Secret`).

![WhatsApp Image 2025-05-17 at 23 34 42 (3)](https://github.com/user-attachments/assets/a76a29a3-5325-452e-b163-5f7907c8e133)

Cole a chave API do Notion aqui:

---

## 5. Crie uma nova página no Notion e configure a conexão

- Crie uma nova página no workspace criado
- Clique no **ícone de lápis** no canto superior direito
- Clique nos **três pontinhos** no canto superior direito da página
- Role para baixo e clique em **Conexões**


<img src="https://github.com/user-attachments/assets/87213e4c-f053-4916-83cc-af20f0d963a3" width="300">

<img src="https://github.com/user-attachments/assets/c24aabcd-e7c4-453b-ad1d-8f6d046b25d3" width="300">

<img src="https://github.com/user-attachments/assets/419a0a47-a85b-45f3-9675-190c921dbc34" width="300">
---

## 6. Autorize a integração

- Digite o nome da sua integração na barra de pesquisa
- Selecione e confirme que ela poderá acessar a página

![WhatsApp Image 2025-05-17 at 23 34 42 (7)](https://github.com/user-attachments/assets/43ece2c7-88ba-48f3-ad31-e60da776e8d0)

![WhatsApp Image 2025-05-17 at 23 34 42 (8)](https://github.com/user-attachments/assets/285df72e-e42b-471d-a5ae-09aecaa39ec8)

---

## 7. Finalize a conexão

Depois de colar as duas chaves necessárias (Google e Notion), clique em **Prosseguir**.


