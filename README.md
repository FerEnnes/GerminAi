# 🌱 GerminAI: Chatbot para Agricultura Sintrópica Baseado em Ernst Götsch

**GerminAI** é um assistente inteligente desenvolvido para ajudar produtores, estudantes e entusiastas da agricultura sintrópica a planejarem e executarem sistemas agroflorestais regenerativos, seguindo os princípios de Ernst Götsch. A ferramenta utiliza modelos de linguagem (LLMs) e APIs geográficas para gerar planos personalizados de agrofloresta com base na localização, clima, solo, relevo e objetivos de cada usuário.

---

## 🧬 O que é Agricultura Sintrópica?

A agricultura sintrópica é uma abordagem inovadora que integra produção agrícola com regeneração ambiental. Criada por Ernst Götsch, ela se baseia na observação dos processos naturais e na cooperação entre plantas, seres humanos e o ecossistema. Diferente da agricultura convencional, que extrai e degrada, a sintrópica promove **vida, diversidade, equilíbrio e abundância**.

### 🌍 Por que é importante?

- Reverte processos de degradação ambiental.
- Cria solos férteis e resilientes sem uso de agrotóxicos.
- Gera alimentos saudáveis e sistemas produtivos biodiversos.
- Sequestra carbono e contribui para o combate às mudanças climáticas.

---

## 🚨 Problema

Apesar de seus inúmeros benefícios, a agricultura sintrópica enfrenta **grandes desafios de disseminação**, principalmente por:

- Falta de tecnologias acessíveis e interativas que ensinem o método de forma simples e didática.
- Escassez de dados organizados e integrados voltados para essa prática.
- Dificuldade em obter recomendações específicas de espécies e técnicas adaptadas ao local do produtor.

---

## 🎯 Objetivo do GerminAI

Oferecer uma **interface inteligente e acessível**, onde qualquer pessoa possa:

- Informar suas condições locais (como localização, relevo, clima, tipo de solo e objetivo).
- Receber um **plano personalizado de agricultura sintrópica**, incluindo:
  - Diagnóstico ecológico
  - Recomendações de espécies por estrato e função
  - Estratégia de plantio e consórcios
  - Cronograma de podas e manejos
  - Sugestões de leitura e aprendizado

---

## 🧠 Arquitetura e Tecnologias Usadas


## 🌐 Desenvolvimento no Google Colab

A versão inicial e interativa do projeto está disponível no Google Colab:

🔗 [GerminAI no Google Colab](https://colab.research.google.com/github/FerEnnes/GerminAi/blob/main/GerminAI.ipynb)

Esse notebook foi desenvolvido como protótipo funcional para testes e refino da lógica antes da implementação da interface no Streamlit.

### ⚙️ Como o Notebook está Estruturado

O notebook é dividido em células com blocos de código Python bem comentados e organizados para guiar o usuário passo a passo na criação de um plano agroflorestal.

#### 1. **Importações**
São feitas importações essenciais, incluindo:

```python
import re
import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
```

Essas bibliotecas permitem:
- Realizar requisições para APIs (OpenStreetMap, IBGE, OpenMeteo, Google Scholar, Google Calendar)
- Buscar e parsear HTML de resultados do Google
- Autenticar e interagir com a agenda do Google via API

#### 2. **Entrada Guiada de Dados**
Coleta informações do(a) agricultor(a) por meio de `input()`:

```python
local_input = input(" Qual é a sua localização? (Cidade/UF, CEP ou latitude,longitude): ")
# outros inputs como tamanho_area, relevo, sombra, objetivo, etc.
```

Esses dados são usados para diagnosticar o local e personalizar as recomendações.

#### 3. **Geolocalização com Diagnóstico Inteligente**
Função `geolocalizar_diagnostico_completo()`:
- Detecta coordenadas (latitude e longitude) a partir de endereço ou CEP via [Nominatim](https://nominatim.org/)
- Faz `reverse lookup` para obter cidade/estado/país
- Chama a [API de Municípios do IBGE](https://servicodados.ibge.gov.br/) para buscar microrregião e região geográfica
- Estima o bioma e tipo de solo com base no estado ou latitude

Saída esperada:

```
🌍 Localização reconhecida: Camboriú, Santa Catarina, Brasil
🗺️ Bioma estimado: Mata Atlântica
🧱 Tipo de solo provável: latossolo vermelho com matéria orgânica
🌐 Coordenadas: -27.02, -48.63
📌 Fonte: Nominatim (OpenStreetMap), IBGE API
```

#### 4. **Agente de Clima**
Busca o clima atual com base nas coordenadas, usando a [API Open-Meteo](https://open-meteo.com/).

#### 5. **Banco de Conhecimento Local**
Um dicionário Python chamado `conhecimento_local` contém princípios e técnicas da agricultura sintrópica, estruturado por tema (princípios, manejo, poda, cobertura do solo, etc.).

A função `buscar_no_banco_local(pergunta)` analisa a pergunta do usuário e retorna trechos relevantes do dicionário.

#### 6. **Buscadores Externos**
Funções auxiliares fazem scraping para trazer referências externas:
- `buscar_artigos_scholar(pergunta)` → busca no Google Scholar
- `buscar_no_site_gotsch(pergunta)` → busca no site oficial do Ernst Götsch via Google

#### 7. **Geração de Resposta Didática**
A função `gerar_resposta_final()` organiza todos os dados coletados e monta um prompt completo para enviar à API do Gemini da Google, pedindo a geração de um plano detalhado com:
- Diagnóstico
- Estratégia de plantio
- Espécies
- Cronograma
- Cuidados iniciais

#### 8. **Agendamento Dinâmico no Google Calendar**
Após a geração da resposta, o usuário pode selecionar eventos (plantio, poda, adubação) e adicioná-los à sua agenda do Google.

Essa etapa usa a API Google Calendar e requer autenticação OAuth2 com um arquivo `client_secret.json`.


### Backend

- **Python 3.12**
- **Google Gemini API** (modelo: `gemini-2.0-flash`)
- **APIs Externas**:
  - OpenStreetMap (Nominatim) para geolocalização
  - IBGE e MapBiomas (via scraping e heurísticas) para inferência de biomas
  - Open-Meteo para clima atual
  - Google Scholar para busca de artigos
  - Google Calendar API para agendamentos

### Interface

- **Streamlit**: Framework leve para criação de apps web com Python
- **UI customizada com emojis e estilo naturalista**

---

## 📦 Instalação Local

```bash
git clone https://github.com/FerEnnes/GerminAi.git
cd GerminAi
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔒 Proteção de Chaves e Segurança

- As chaves da API Gemini e Google Calendar estão **carregadas por variáveis de ambiente** via `.streamlit/secrets.toml` ou arquivos `.env` (recomendado no deploy).
- O `.gitignore` bloqueia arquivos sensíveis como `client_secret.json` e `token.json`.

---

## 🚀 Como Publicar

A aplicação pode ser publicada gratuitamente no [Streamlit Cloud](https://streamlit.io/cloud). Basta:

1. Subir o código para o GitHub.
2. Criar um app no Streamlit Cloud.
3. Adicionar as chaves no menu **Secrets**.
4. Compartilhar o link com o mundo 🌎

---

## 👩‍🔬 Exemplos de Uso

```plaintext
Localização: Camboriú, SC
Área: 2000m²
Objetivo: Alimentação e restauração
Espécies: Frutíferas e Leguminosas

➡ Resultado: Diagnóstico do local + plano personalizado + recomendações de podas + sugestões de leitura.
```

---

## 📄 Estrutura de Arquivos

```
├── app.py                # Interface Streamlit
├── germinai_backend.py   # Toda a lógica e agentes
├── requirements.txt      # Dependências do projeto
├── .gitignore            # Ignora arquivos sensíveis
├── .streamlit/
│   └── config.toml       # Configuração de layout
```

---

## 🤝 Autoria

Projeto idealizado por **Fernanda Müller Ennes**  
Estudante de Análise e Desenvolvimento de Sistemas e entusiasta da agricultura regenerativa, dados e IA.

---

## 📢 Contribuições Futuras

- Inclusão de imagens por satélite via MapBiomas
- Sugestão automática de consórcios ideais
- Expansão para outros idiomas
- Integração com WhatsApp ou Telegram

---

## Links importantes: 
-Chatbot do GerminAi:
-Link do notebook no Colab: https://colab.research.google.com/drive/1jw3d4pvQktIBZ4VzM-gKoCJKn8NUOKxm?usp=sharing

> “Não basta plantar árvores. É preciso plantar ideias.” 🌱
