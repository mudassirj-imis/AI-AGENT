from agents import agent
from browser import start_browser, login

async def main():
response = agent.invoke("List the number of beneficiaries in MUMTA Program")

print(response)