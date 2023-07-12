from flask import request, jsonify, abort
from io import BytesIO
import boto3
from utils.openai_util import ChatOpenAI
from utils.session_util import SessionManager
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from urllib.parse import urlparse
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.utilities import SerpAPIWrapper
from langchain import OpenAI, LLMChain
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, AgentType, initialize_agent
import os

load_dotenv()
llm = ChatOpenAI(temperature=0.8)
session_manager = SessionManager()
# pinecone = PineconeManager()

search = SerpAPIWrapper()

def memory_conversational_chat(body):
    session_id = request.headers.get("session-id") if request.headers.get("session-id") is not None else body.get('session_id')
    if session_id is None:
        return {"response": "Bad Request: session_id is missing"}
    try:
        message_history = session_manager.get_conversation_memory(session_id)
        print(message_history)
        # body = request.get_json()
        user_input = body.get("message")

        message_history.add_user_message(str({"role": "user", "content": user_input}))
        db_chain = session_manager.getdb_connection()

        tools = [
            Tool(
                name="Current Search",
                func=search.run,
                description="useful for when you need to answer questions about current events or the current state of the world"
            ),
            Tool(
                name = "Agents Database",
                func = db_chain.run,
                description = "useful to fetch the agents info and their about information"
            ),
            Tool(
                name = "Event rooms",
                func = db_chain.run,
                description = "useful to fetch the scheduled rooms information"
            ),
            Tool(
                name = "Property Data",
                func = db_chain.run,
                description= "A Property search engine. Use this more than the normal search if the question is about Realestate, like 'who is the property details?', when it fails to get answer from this search engine. If you colund't find the answer using this tool use the current search"
            )
        ]
        prefix = """Radius Agent Bot, powered by AI, is here to assist you on behalf of the Radius Support Team. Radius Agent is an online real estate brokerage focused on helping agents succeed. Agents keep 100% of their commissions while getting 100% support from the Radius team. Agents can use our tools even if they're with another brokerage. If I don't have the answer you're looking for, don't worry! I'm constantly learning and can be trained to improve. I strive to do better with each conversation. Please feel free to ask any questions, and I will provide you with the best answers using the following tools:"""
        suffix = """Begin!"

        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "agent_scratchpad"]
        )

        # memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=message_history)

        llm_chain = LLMChain(llm=OpenAI(model_name = "gpt-4", temperature=0), prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        response = agent_chain.run(user_input)

        message_history.add_ai_message(str({"role": "bot", "content": response}))

        response_data = {
            "response": response,
        }
        return response_data
    except Exception as e:
        response = str(e)
        if response.startswith("Could not parse LLM output: `"):
            response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
            response_data = {
                "response": response,
            }
            return response_data
        else:
            error_response = {
                "response": str(e),
            }
            return error_response

def pdf_reader(body):

    # body = request.get_json()
    pdf_url = body.get("pdf_url")
    if pdf_url is not None:
        s3 = boto3.client("s3", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        bucket, key = parse_s3_url(pdf_url)

        obj = s3.get_object(Bucket=bucket, Key=key)
        fs = obj['Body'].read()
        pdf_reader = PdfReader(BytesIO(fs))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # create embeddings
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        # show user input
        user_question = body.get("question")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)

            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=user_question)
            response_data = {
            "response": response,
            }
            return response_data

def parse_s3_url(pdf_url):
    parsed_url = urlparse(pdf_url)
    bucket = parsed_url.netloc.split('.')[0]
    key = parsed_url.path.lstrip('/')

    return bucket, key
