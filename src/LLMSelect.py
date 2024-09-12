from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
load_dotenv()

class LLMSelector:
    @staticmethod
    def get_llm(api_provider, model_name):
        '''
        input: 
            api_provider: str
            model_name: str
        ouput: 
            ChatModel
        '''
        if api_provider == "google":
            return ChatGoogleGenerativeAI(model=model_name)
        elif api_provider == "groq":
            if model_name == "mixtral-8x7b-32768-groq":
                model_name = "mixtral-8x7b-32768"
            return ChatGroq(model=model_name)
        elif api_provider == "openai":
            return ChatOpenAI(model=model_name)
        elif api_provider == "anthropic":
            return ChatAnthropic(model_name=model_name)
        elif api_provider == "mistralai":
            return ChatMistralAI(model_name=model_name)
        else:
            raise ValueError(f"Unsupported API provider: {api_provider} and model: {model_name}")