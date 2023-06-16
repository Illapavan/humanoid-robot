from flask import request, jsonify
from utils.openai_util import ChatOpenAI
from utils.session_util import SessionManager
from utils.pinecone_utils import PineconeManager
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain import OpenAI, LLMChain
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor


llm = ChatOpenAI(temperature=0.8)
session_manager = SessionManager()
pinecone = PineconeManager()

search = SerpAPIWrapper()



def memory_conversational_chat():
    session_id = request.headers.get("session-id")
    message_history = session_manager.get_conversation_memory(session_id)
    body = request.get_json()
    user_input = body.get("message")

    message_history.add_user_message(str({"role": "user", "content": user_input}))

    tools = [
        Tool(
            name="Current Search",
            func=search.run,
            description="useful for when you need to answer questions about current events or the current state of the world"
        ),
    ]
    prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
    suffix = """Begin!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=message_history)


    llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)
    response = agent_chain.run(user_input)

    message_history.add_ai_message(user_input)

    response_data = {
        "response": response,
    }

    return jsonify(response_data)   



    # agent_chain = initialize_agent(create_tools(), llms, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
    # answer = agent_chain.run(user_input)
    # print(answer)

    return ""

    pinceConeData = pinecone.getPineConeInstance()
    pine_cone_result = pinceConeData.similarity_search(user_input)
    filtered_results = []
    for result in pine_cone_result:
        if result.score >= 0.8:
            filtered_results.append(result.document.page_content)
    print(filtered_results)

    return ""

    # langchain agent
    agent = Agent()

    tools = {"pinecone": pine_cone_result, "redis": conversation_memory }
    response = agent.generate_response(conversation_memory, user_input, tools=tools)
    print(response)
    return ""

    # Generate a response from the model using conversational memory
    response = llm.generate_response(conversation_memory, user_input)

    
