"""
Pipelined - Implemented on open web ui for candidate CV evaluation through LLM

1. Add requirements into the chat --> until it gets verified
2. Add CV's --> create a knowledge base from the CV's and return the explicit llm call given as default
3. Use the chat to ask necessary informations based on the knowledge base

"""

from typing import List, Union, Generator, Iterator, Optional
from pydantic import BaseModel, Field
from typing import List
from typing import List, Union, Generator, Iterator
from typing import ClassVar
import os
from typing import List
from pydantic import BaseModel, Field



################################################# PIPE CLASS #################################################
class Pipeline:
    """
    Pipeline implementation using Open Web UI for candidate CV evaluation via Large Language Models (LLMs).

    Workflow:
        

    Initialization:
    
    Features:
        

    Version:
        - 2.0.0
    """
    
    class Valves(BaseModel):
        """
        Configuration container class for storing constants related to
        API endpoints, model settings, debugging flags, and file paths.

        These values are used globally throughout the agent pipeline.
        """
        ################################################# Configuration #################################################
        # Base URLs
        TOKEN: str 
        OPEN_WEB_UI_BASE_URL: str 
        OLLAMA_BASE_URL: str 
        OPENAI_BASE_URL: str 
        MODEL: str 

        # Debugging and processing settings
        DEBUG: bool = False
        NUM_RE_PROCESS: int 

        # SQLite database path for storing chat metadata
        DB_PATH: ClassVar[str] = r"K_HR.db"
        """Relative path to the SQLite database for storing chat states and metadata."""

    def __init__(self):
        """
        Initializes the pipeline class.

        This method runs only once when the pipeline is activated 
        (e.g., when the backend server restarts or reinitializes the agent).

        It sets up default values for state management, token authentication,
        memory structures, and existing file tracking.
        """
        print('*' * 10 + "CLASS PIPE CALLED" + '*' * 10)

        # Load configuration parameters
        self.valves = self.Valves(
            **{
                "TOKEN": os.getenv("TOKEN", ""),
                "OPEN_WEB_UI_BASE_URL": os.getenv("OPEN_WEB_UI_BASE_URL", "http://localhost:8080/api/v1"),
                "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://localhost:8080/ollama"),
                "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://localhost:8080/openai"),
                "MODEL": os.getenv("MODEL", "DeepSeek-R1-0528-Qwen3-8B-Q2_K_L.gguf"),
                "DEBUG": os.getenv("DEBUG_MODE", "false").lower() == "true",
                "NUM_RE_PROCESS": os.getenv("NUM_RE_PROCESS", 1),
            }
        )

        # Agent name identifier
        self.name = "Agentic_HR"
        self.token = self.valves.TOKEN


        # Runtime memory to temporarily store parsed requirements by chat -> no need after DB integration
        self.memory_requirments_dict = {}

        # Count files already available in knowledge base
        #self.file_count = len(self.get_file_names_ids(self.token))

        # Mapping from chat IDs to knowledge base IDs
        self.chatids_to_knowledgeids = {}

        # Store evaluation results of candidates
        self.evaluation_results = {}

        # Set initial internal state of the agent
        self.state = "REQUIRMENTS_UPDATE" #within the pipe function it checks and update
        
    async def on_startup(self):
        # This function is called when the server is started.
        print(f"AGENT_ON:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is shutdown.
        print(f"AGENT_ON:{__name__}")
        pass
        
        
    def debug(self, *args, **kwargs):
        """
        Prints debug messages if DEBUG mode is enabled in the valves configuration.
        Parameters:
            - *args, **kwargs: Variable argument messages to be printed.
        """
        if self.valves.DEBUG:
            print(*args, **kwargs)
    ################################################ pipe ######################################################
# ----------------------------------------------------------------------------
# pipe function is going to run always when a new message is being prompted
# ----------------------------------------------------------------------------

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        """
        Main pipeline function that processes user messages and routes them through
        different states such as requirements input, CV processing, or general chat.

        Parameters:
        - user_message (str): User input typed in the UI.
        - model_id (str): Model ID selected for inference (e.g., openai/gpt-4, llama3).
        - messages (List[dict]): Contextual chat history including system, user, and assistant messages.
        - body (dict): Additional Open WebUI settings (e.g., streaming config, max tokens, temperature).

        Returns:
        - Union[str, Generator, Iterator]: Streamed or final model response.
        """
        # ----------------------------------------------------------------------------
        # DEBUG AND PIPE ACTIVATION LOG
        # ----------------------------------------------------------------------------
        
        print(body)
        
        if self.valves.DEBUG:
            print("------------------DEBUG MODE : ON--------------------", '\n')
        else:
            print("------------------DEBUG MODE : OFF--------------------", '\n')

        self.debug("PIPE FUNCTION ACTIVATED")
        self.token =  self.valves.TOKEN
        self.debug('-' * 50)
        self.debug(f"api_key :{self.token}")
        self.debug('-' * 50)
        print(f"pipe:{__name__}")
        self.debug('-' * 50)
        user_id = (body["user"]["id"])
        self.debug(f"user_id :{user_id}")
        self.debug('-' * 50)
        # ----------------------------------------------------------------------------
        # INITIAL STATE AND FILE COUNT CHECKING
        
        return user_message