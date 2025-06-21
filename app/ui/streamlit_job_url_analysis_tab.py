import streamlit as st
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ui.agent_manager import AgentManager
from ui.utils import UIUtils
from job_details_agent import run_agent as run_job_analysis_agent

class StreamlitJobUrlAnalysisTab:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.utils = UIUtils()
        self.job_results_path = Path("Jobs/Job_Results")
        
        self.job_results_path.mkdir(parents=True, exist_ok=True)

    def _run_async_in_thread(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result