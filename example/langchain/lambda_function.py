import warnings
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import HumanMessage


warnings.filterwarnings("ignore", category=DeprecationWarning) 

chat = BedrockChat(model_id="anthropic.claude-3-sonnet-20240229-v1:0", model_kwargs={"temperature": 1})


def lambda_handler(event, context):
    messages = [
        HumanMessage(
            content="How do you configure an Amazon VPC?"
        )
    ]
    response = chat(messages).content
    return response
