import asyncio

from langchain.messages import HumanMessage
from browser import (start_browser, login, get_screenshot_description, close_browser, get_radio_inputs,click_radio_by_label,get_sidebar_links)
from utils import process_image
from agents import agent
import warnings 

warnings.filterwarnings("ignore")

async def main():
    await start_browser()

    await login(
        url="https://api.imis.com.pk:9001",
        username="admin_imis@yopmail.com",
        password="Intra$12345"
    )

    

    # screen_shot, dom = await take_screenshot_dom()
    # print(screen_shot[:100])
    # print("\n\n")
    # screenshot_b64 = process_image(screen_shot)

    question = input("Enter your question: " + ".")
    print("Question: ", question)
    print("")
    #response, dom = await get_screenshot_description(question)
    #print("Agent Response: ", response)
    print("\n\n")
    anget_r = await agent.ainvoke({"messages": [HumanMessage(question)]})
    print("Agent Response: ", anget_r['messages'][-1].content)
    # await click_radio_by_label("MUMTA")
    
    # side_bar_links = await get_sidebar_links()
    # print("Sidebar Links: ", side_bar_links)
    # await close_browser()
    

asyncio.run(main())