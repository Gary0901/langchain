import os
from dotenv import load_dotenv
import getpass
from typing import Sequence, TypedDict, Annotated
import operator

# 載入 .env 檔案中的環境變數
load_dotenv()

# 現在你可以透過 os.environ 或 os.getenv() 來讀取這些變數
langsmith_tracing = os.getenv("LANGSMITH_TRACING")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

if not os.getenv("GOOGLE_API_KEY"):
   os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

# 從正確的模組匯入 ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langchain_core.messages import SystemMessage, trim_messages

model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

trimmer = trim_messages(
    max_tokens = 65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# Define a new graph 
workflow = StateGraph(state_schema=State)

# Define the function that calls the model
def call_model(state: State):
    print(f"Message before trimming:{len(state['messages'])}")
    trimmed_messages = trimmer.invoke(state["messages"])
    print(f"Messages after trimming: {len(trimmed_messages)}")
    print("Remaining messages:")
    for msg in trimmed_messages:
        print(f"  {type(msg).__name__}: {msg.content}")
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": [response]}

# Define the (single) node in the graph 
workflow.add_edge(START,"model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

""" # 執行第一次對話
# 執行第一次對話
print("### 執行第一次對話 (thread_id: abc123)")
config = {"configurable": {"thread_id": "abc123"}}
output = app.invoke({"messages": [HumanMessage(content="Hi! I'm Bob")]}, config)
print(output["messages"][-1].content)
print("-" * 20)

# 執行第二次對話 (在同一個 thread_id 下)
print("### 執行第二次對話 (thread_id: abc123)")
output = app.invoke({"messages": [HumanMessage(content="What's my name?")]}, config)
print(output["messages"][-1].content)
print("-" * 20)

# 執行新的對話 (新的 thread_id)
print("### 執行新的對話 (thread_id: abc234)")
config_new = {"configurable": {"thread_id": "abc234"}}
output = app.invoke({"messages": [HumanMessage(content="What's my name?")]}, config_new)
print(output["messages"][-1].content) """



""" config = {"configurable": {"thread_id": "abc456"}}
query = "Hi! I'm Bob."
language = "Chinese"

input_messages = [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages, "language": language},
    config,
)
output["messages"][-1].pretty_print()

query = "What is my name?"

input_messages = [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages},
    config,
)
output["messages"][-1].pretty_print() """



messages = [
    SystemMessage(content="you're a good assistant"),
    HumanMessage(content="hi! I'm bob"),
    AIMessage(content="hi!"),
    HumanMessage(content="I like vanilla ice cream"),
    AIMessage(content="nice"),
    HumanMessage(content="whats 2 + 2"),
    AIMessage(content="4"),
    HumanMessage(content="thanks"),
    AIMessage(content="no problem!"),
    HumanMessage(content="having fun?"),
    AIMessage(content="yes!"),
]

trimmer.invoke(messages)

config = {"configurable": {"thread_id": "abc567"}}
query = "What is my name and how old am I and what food do i like?"
language = "English"

input_messages = messages + [HumanMessage(query)]
""" output = app.invoke(
    {"messages": input_messages, "language": language},
    config,
)

print("\n模型回應:")
print(output["messages"][-1].content) """

print("模型正在串流回應:")
for chunk, metadata in app.stream(
    {"messages": input_messages, "language": language},
    config,
    stream_mode="messages",
):
    if isinstance(chunk, AIMessage):  # 過濾，只顯示來自 AI 的訊息
        print(chunk.content, end="")  # 使用 end="" 讓輸出不換行
print("\n")

