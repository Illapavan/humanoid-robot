from flask import request, jsonify, abort
from io import BytesIO
import boto3
from langchain.chat_models import ChatOpenAI
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
                name="Google Search Engine",
                func=search.run,
                description="This tool is used for general search related queries. use this tool if you failed to get results from other tools more"
            ),
            Tool(
                name = "Property Data",
                func = db_chain.run,
                description= "This tool is used for realestate related queries about availabilty of property related queries. If failed to load any info fetch the result from the google"
            )
        ]
        # prefix = """You are a Radius Agent Bot, powered by AI, here to assist on behalf of the Radius Support Team. Radius Agent is an online real estate brokerage focused on helping agents succeed. If you don't have the answer you're looking for, don't worry!. You have memory use that to reply if that doesn't helps. Just reply you dont know. Be polite"""
        # suffix = """Begin!
        # Question: {input}
        # Action : {agent_scratchpad}"""

        # prompt = ZeroShotAgent.create_prompt(
        #     tools,
        #     prefix=prefix,
        #     suffix=suffix,
        #     input_variables=["input", "agent_scratchpad"]
        # )

        memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=message_history)

        # llm_chain = LLMChain(llm=OpenAI(model_name = "gpt-3.5-turbo-16k", temperature=0), prompt=prompt)
        # agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        # agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory = memory, handle_parsing_errors=True)
        # response = agent_chain.run(user_input)
        my_agent = initialize_agent(
            tools=tools,
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k"),
            agent='conversational-react-description',
            verbose=True,
            memory=memory,
            max_iterations=3,
            early_stopping_method='generate',
            handle_parsing_errors="Check your output and make sure it conforms!",
        )
        response = my_agent.run(user_input)

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
                "response": str(e)
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

            llm = OpenAI(model_name = "gpt-3.5-turbo-16k", temperature=0, verbose=True)
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
