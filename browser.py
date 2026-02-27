from playwright.async_api import async_playwright
import asyncio
from langchain.tools import tool

from ai import ask_question
from utils import process_image

browser = None
page = None


async def start_browser(headless: bool = False):
    global browser, page
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    page = await browser.new_page()
    print("Browser started!")


async def login(url: str, username: str, password: str):
    global page
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")
    await page.get_by_placeholder("Enter your email").fill(username)
    await page.locator("input[type='password']").fill(password)
    await page.get_by_role("button", name="Login").click()
    await asyncio.sleep(5)
    # Wait for URL to change away from login page
    #await page.wait_for_url(lambda url: "login" not in url, timeout=10000)
    await page.wait_for_load_state("networkidle")
    print("Logged in successfully!")


async def take_screenshot_dom():
    global page
    screenshot_bytes = await page.screenshot(full_page=True)
    dom = []
    elements = await page.query_selector_all("button, a, input, select, textarea")
    for el in elements:
        dom.append({
            "type": await el.evaluate("e => e.tagName.toLowerCase()"),
                "text": await el.inner_text() or await el.get_attribute("value") or "",
                "id": await el.get_attribute("id"),
                "classes": await el.get_attribute("class")
                        })
    
    return screenshot_bytes, dom

@tool("Get_Screenshot_Description")
async def get_screenshot_description(question: str):
    """ Capture the screenshot and DOM, and ask the AI model to analyze it and provide instructions to the user based on the question."""
    print("LOG: Get Screenshot Description")
    screenshot,dom = await take_screenshot_dom()
    screenshot_b64 = process_image(screenshot)
    description = await ask_question(question, screenshot_b64, dom)
    url = "Current URL: " + str(page.url)
    print(url)
    return description.content


async def get_radio_inputs():
    """ Get all radio inputs and their associated labels on the current page."""
    global page
    radios = await page.locator("input[type='radio']").all()
    for i, radio in enumerate(radios):
        # Get the exact next h6 after each radio
        label = await radio.locator("xpath=following::h6[1]").inner_text()
        print(f"Radio {i}: value={await radio.get_attribute('value')} | label={label}")
    return radios

@tool("Select_Program")
async def click_radio_by_label(label_text: str):
    """Select a Program by clicking a radio button based on the text of its associated label. Then Select & Continue button to proceed."""
    print("LOG: Click Radio")
    global page
    radios = await get_radio_inputs()
    url = "Current URL: " + str(page.url)
    print(url)
    for i, radio in enumerate(radios):
        label = await radio.locator("xpath=following::h6[1]").inner_text()
        if label_text.lower() in label.lower():
            await radio.click()
            print(f"Clicked radio with label: {label}")
            break
            
    # Find and click Select & Continue button
    await page.get_by_role("button", name="Select & Continue").click()
    await page.wait_for_load_state("networkidle")
    print("Clicked Select & Continue!")


async def get_sidebar_links():
    """ Get all links in the sidebar of the current page."""
    global page
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(5)
    # Wait for sidebar to appear
    await page.wait_for_selector("nav, aside, [class*='sidebar'], [class*='side-bar'], [id*='sidebar']")

    # Get all links inside sidebar
    links = await page.locator("nav a, aside a, [class*='sidebar'] a, [class*='side-bar'] a, [id*='sidebar'] a").all()
    url = "https://api.imis.com.pk:9001"
    sidebar_links = []
    for i, link in enumerate(links):
        text = await link.inner_text()
        href = await link.get_attribute("href")

        if text.strip() and href:  # skip empty links
            sidebar_links.append({"text": text.strip(), "href": url + href})
            print(f"Link {i}: text={text.strip()} | href={href}")

    return sidebar_links

@tool("Go_to_Sidebar_URL")
async def goto_sidebar_url(label_text: str):
    """ Navigate to the sidebar link according to the user requirements"""
    print("LOG: Goto SIdebar URL")
    
    sidebar_links = await get_sidebar_links()
    for link in sidebar_links:
        if label_text.lower() in link["text"].lower() and link["href"] is not None:
            await page.goto(link["href"])
            print(f"Navigated to sidebar link: {link['text']}")
            break
    url = "Current URL: " + str(page.url)
    print(url)

async def close_browser():
    global browser
    await browser.close()
    print("Browser closed!")

