from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware, SummarizationMiddleware, ModelFallbackMiddleware
from browser import get_screenshot_description, click_radio_by_label,goto_sidebar_url
from ai import get_llm,get_fallback_llm

tools = [get_screenshot_description, click_radio_by_label,goto_sidebar_url]

SYS_PROMPT = """You are an assistant that can interact with a web browser to perform tasks based on user queries. You have access to the following tools: get_screenshot_description, click_radio_by_label, goto_sidebar_url. Use these tools to navigate and interact with web pages to find the information needed to answer user questions.

Tools Description:
1. get_screenshot_description(question): Takes a screenshot of the current webpage and provides a description of the page along with its DOM structure based on the provided question.
2. click_radio_by_label(label_text): Select a Program by clicking a radio button based on the text of its associated label. Then Select & Continue button to proceed.
3. goto_sidebar_url(label_text): Navigate to the sidebar link according to the user requirements.

From the sidebar URLs filter out the URLs according to the user query and then navigate to the required page from filtered URLs.
Do not overthink on gotoSidebarURL tool and do not use get_screenshot_description tool on every page. Use it only when you need to find some specific information on the page or when you are not sure about the next step to take. Always try to use click_radio_by_label and goto_sidebar_url tools first to navigate through the website and find the required information.

1. The workflow is that first select and open a Program Dashboard e.g. Laptop
2. Then click on the sidebar link according to the user requirements e.g. Beneficiaries
3. Then use get_screenshot_description to find the required information on the page

Notes:
Program is selected first and then it cannot be changed.
First Focus on the Navigation then use screenshot if data on the screenshot is not according to the user then go to the most appropiate Sidebar URL and then use screenshot to find the required data on that page.
Check the screenshot description after each run, if the user requirements are fulfilled then stop and respond.
"""

fallback_llm = get_fallback_llm()
agent = create_agent(tools=tools, 
                     model=get_llm(), 
                     system_prompt=SYS_PROMPT,
                     middleware=[
        SummarizationMiddleware(
            model=fallback_llm,
            trigger=("tokens", 7900),
            keep=("messages", 20),
        ),
        ModelFallbackMiddleware(
            get_fallback_llm()
        ),
        ToolCallLimitMiddleware(
            tool_name="Select_Program",
            thread_limit=5,
            run_limit=1,
        ),
    ],
    
    ) 