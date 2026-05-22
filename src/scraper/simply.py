from playwright.async_api import Page, BrowserContext
from patchright.async_api import async_playwright

from pathlib import Path

from scraper.utils.checkpoint import save_checkpoint, load_checkpoint, clear_checkpoint
from scraper.utils.human import (
    MouseState,
    random_pause,
    human_move_and_click,
    human_move_and_click_locator,
    human_type,
    human_scroll,
)
from scraper.utils.io import write_json, sanitize_filename
from scraper.utils.parser import extract_management_and_ownership

import asyncio
import json
import logging
import random


LOGGER = logging.getLogger(__name__)


async def browse_company_page(page: Page) -> None:
    engagement = random.choices(
        ["light", "medium", "deep"],
        weights=[0.3, 0.5, 0.2]
    )[0]

    if engagement == "light":
        await random_pause(1.0, 2.0)
        await human_scroll(page, scroll_distance=random.randint(150, 300))
        await random_pause(0.8, 1.5)

    elif engagement == "medium":
        await random_pause(1.5, 2.5)
        await human_scroll(page, scroll_distance=random.randint(300, 500))
        await random_pause(1.0, 2.0)
        await human_scroll(page, scroll_distance=random.randint(150, 300))
        await random_pause(0.8, 1.5)
        await human_scroll(page, scroll_distance=-random.randint(100, 200))
        await random_pause(1.0, 2.0)

    elif engagement == "deep":
        await random_pause(2.0, 3.5)
        await human_scroll(page, scroll_distance=random.randint(400, 600))
        await random_pause(1.5, 3.0)
        await human_scroll(page, scroll_distance=random.randint(200, 400))
        await random_pause(2.0, 4.0)
        await human_scroll(page, scroll_distance=-random.randint(150, 350))
        await random_pause(1.0, 2.5)
        await human_scroll(page, scroll_distance=random.randint(100, 300))
        await random_pause(1.5, 2.5)


async def interact_with_show_more_buttons(
    page: Page,
    mouse_state: MouseState
) -> None:
    expandable_buttons = [
        '[data-cy-id="copy-truncator-show-more"]',
        '[data-cy-id="report-sub-section-leadership-team"] [data-cy-id="truncator-button"]',
        '[data-cy-id="report-sub-section-board-members"] [data-cy-id="truncator-button"]',
        '[data-cy-id="see-more-updates"]',
    ]

    for button_selector in expandable_buttons:
        try:
            button = page.locator(button_selector)
            is_visible = await button.is_visible()

            if not is_visible:
                continue

            if random.random() < 0.5:
                await button.scroll_into_view_if_needed()
                await random_pause(0.5, 1.5)
                await human_move_and_click(page, button_selector, mouse_state)
                await random_pause(0.8, 2.0)

        except Exception:
            continue


async def read_management_page(page: Page, mouse_state: MouseState) -> None:
    reading_depth = random.choices(
        ["skim", "read", "thorough"],
        weights=[0.3, 0.5, 0.2]
    )[0]

    if reading_depth == "skim":
        await random_pause(1.0, 2.0)
        await human_scroll(page, scroll_distance=random.randint(100, 200))
        await random_pause(0.8, 1.5)

    elif reading_depth == "read":
        await random_pause(2.0, 3.5)
        await human_scroll(page, scroll_distance=random.randint(200, 350))
        await random_pause(1.5, 3.0)
        await human_scroll(page, scroll_distance=random.randint(100, 200))
        await random_pause(1.0, 2.0)

    elif reading_depth == "thorough":
        await random_pause(3.0, 5.0)
        await human_scroll(page, scroll_distance=random.randint(300, 450))
        await random_pause(2.0, 4.0)
        await human_scroll(page, scroll_distance=random.randint(150, 300))
        await random_pause(2.5, 4.5)
        await human_scroll(page, scroll_distance=-random.randint(150, 250))
        await random_pause(1.5, 3.0)

    await interact_with_show_more_buttons(page, mouse_state)


async def browse_detour_tabs(page: Page, mouse_state: MouseState) -> None:
    tabs_before_management = [
        'a[data-cy-id="desktop-sidebar-nav-1"]',
        'a[data-cy-id="desktop-sidebar-nav-3"]',
        'a[data-cy-id="desktop-sidebar-nav-4"]',
        'a[data-cy-id="desktop-sidebar-nav-7"]',
    ]

    should_detour = random.random() < 0.4

    if not should_detour:
        return

    detour_count = random.randint(1, 2)
    selected_tabs = random.sample(tabs_before_management, detour_count)

    for tab_selector in selected_tabs:
        try:
            await human_move_and_click(page, tab_selector, mouse_state)
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
            await random_pause(1.5, 3.5)
            await human_scroll(page, scroll_distance=random.randint(100, 350))
            await random_pause(1.0, 2.5)

        except Exception:
            continue


async def browse_community_narratives(
    page: Page,
    mouse_state: MouseState,
    target_market: str = "sg"
) -> None:
    try:
        nav_community_selector = '[data-cy-id="main-navigation"] a[href="/community/narratives"]'
        await human_move_and_click(page, nav_community_selector, mouse_state)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await random_pause(1.5, 3.0)

        market_switch_selector = f'a[href="/community/narratives/{target_market}"]'
        market_switch_button = page.locator(market_switch_selector)

        is_market_button_visible = await market_switch_button.is_visible()

        if is_market_button_visible:
            await human_move_and_click_locator(page, market_switch_button, mouse_state)
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await random_pause(1.2, 2.5)

        await human_scroll(page, scroll_distance=random.randint(100, 150))
        await random_pause(1.0, 2.5)

        narrative_card_links = page.locator('[role="listitem"] a.flex-1.px-x1')
        await narrative_card_links.first.wait_for(timeout=10000)

        total_cards = await narrative_card_links.count()

        if total_cards == 0:
            LOGGER.info("no narrative cards found, skipping community browse")
            return

        random_card_index = random.randint(0, total_cards - 1)
        selected_card = narrative_card_links.nth(random_card_index)

        await selected_card.wait_for(state="visible", timeout=5000)
        await selected_card.scroll_into_view_if_needed()
        await random_pause(0.3, 0.7)

        await human_move_and_click_locator(page, selected_card, mouse_state)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await random_pause(2.0, 4.0)

        total_down_distance = random.randint(500, 1250)
        chunks = random.randint(3, 6)
        chunk_size = total_down_distance // chunks

        for _ in range(chunks):
            await human_scroll(page, scroll_distance=chunk_size)
            await random_pause(2.5, 6.0)

        scroll_back_distance = random.randint(150, 400)
        await human_scroll(page, scroll_distance=-scroll_back_distance)
        await random_pause(1.0, 3.0)

    except Exception:
        LOGGER.exception("community browse failed, skipping")
        return None 
    

async def run_automation(
    email_address: str,
    account_password: str,
    companies: list[dict[str, str]],
    headless: bool = False
) -> None:
    mouse_state = MouseState(
        x=random.uniform(300, 600),
        y=random.uniform(200, 400)
    )

    async with async_playwright() as playwright_instance:
        browser = await playwright_instance.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        )

        browser_context: BrowserContext = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/147.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
            },
            java_script_enabled=True,
        )

        await browser_context.add_init_script("""
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
                ]
            });

            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };

            Object.defineProperty(screen, 'width', { get: () => 1440 });
            Object.defineProperty(screen, 'height', { get: () => 900 });
            Object.defineProperty(screen, 'availWidth', { get: () => 1440 });
            Object.defineProperty(screen, 'availHeight', { get: () => 860 });
            Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
            Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });

            const original_permissions_query = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : original_permissions_query(parameters)
            );

            const original_to_data_url = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const canvas_context = this.getContext('2d');
                if (canvas_context) {
                    const image_data = canvas_context.getImageData(0, 0, this.width, this.height);
                    for (let index = 0; index < image_data.data.length; index += 100) {
                        image_data.data[index] ^= Math.floor(Math.random() * 3);
                    }
                    canvas_context.putImageData(image_data, 0, 0);
                }
                return original_to_data_url.apply(this, arguments);
            };

            const original_get_parameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return original_get_parameter.apply(this, arguments);
            };
        """)

        page = await browser_context.new_page()

        is_webdriver_exposed = await page.evaluate("navigator.webdriver")
        LOGGER.info("navigator.webdriver: %s", is_webdriver_exposed)

        if is_webdriver_exposed:
            LOGGER.warning("webdriver flag is visible, patchright is not patching correctly")

        LOGGER.info("companies received: %d", len(companies))

        await login_simplywallst(
            page=page,
            email_address=email_address,
            account_password=account_password,
            mouse_state=mouse_state
        )

        await run_simplywallst(
            page=page,
            companies=companies,
            mouse_state=mouse_state
        )

        await browser.close()


async def login_simplywallst(
    page: Page,
    email_address: str,
    account_password: str,
    mouse_state: MouseState
):
    await page.goto("https://simplywall.st/login", wait_until="networkidle")
    await page.wait_for_selector('input[type="email"]', timeout=15000)

    await random_pause(1.0, 1.6)

    await human_move_and_click(page, 'input[type="email"]', mouse_state)
    await human_type(page, email_address)
    await random_pause(0.4, 1.0)

    await human_move_and_click(page, 'input[type="password"]', mouse_state)
    await human_type(page, account_password)
    await random_pause(0.5, 1.2)

    await human_move_and_click(page, 'button[type="submit"]', mouse_state)
    await page.wait_for_url("**/dashboard", timeout=15000)
    await random_pause(1.5, 2.5)

    await random_pause(1.0, 2.0)
    await human_scroll(page, scroll_distance=random.randint(150, 400))
    await random_pause(0.8, 1.8)

    LOGGER.info("Logged in successfully")


async def run_simplywallst(
    page: Page,
    companies: list[dict[str, str]],
    mouse_state: MouseState
):
    existing_checkpoint = load_checkpoint()
    LOGGER.info("raw existing checkpoint: %s", existing_checkpoint)

    if existing_checkpoint is not None:
        current_companies = existing_checkpoint
    else:
        current_companies = companies

    session_size = random.randint(10, 18)
    companies_to_process = current_companies[:session_size]
    remaining_companies = current_companies[session_size:]

    LOGGER.info("Session will process %d companies", session_size)

    random_break_interval = random.randint(3, 5)
    community_browse_probability = 0.3

    for index, company in enumerate(companies_to_process):
        company_name = company.get('name')
        symbol = company.get('symbol')

        LOGGER.info("Searching for: %s | symbol: %s", company_name, symbol.lower())

        try:
            await scrape_single_company(
                page=page,
                company_name=company_name,
                mouse_state=mouse_state,
                symbol=symbol
            )

        except Exception as error:
            LOGGER.exception("Failed for %s: %s", company_name, error, exc_info=True)
            remaining_companies.insert(0, company)
            await page.goto("https://simplywall.st/dashboard", wait_until="domcontentloaded")
            await random_pause(1.5, 2.5)
            continue

        await random_pause(3.0, 6.0)

        is_not_last = index < len(companies_to_process) - 1
        is_break_point = (index + 1) % random_break_interval == 0

        if is_break_point and is_not_last:
            should_browse_community = random.random() < community_browse_probability

            if should_browse_community:
                # await browse_community_narratives(
                #     page=page,
                #     mouse_state=mouse_state,
                # )
                await random_pause(2.0, 4.0)
            
            else:
                LOGGER.info("Taking a plain break after company %d...", index + 1)
                await random_pause(45, 120)

            random_break_interval = random.randint(4, 6)

    if remaining_companies:
        save_checkpoint(remaining_companies)
        LOGGER.info("Checkpoint saved: %d companies remaining", len(remaining_companies))
    
    else:
        clear_checkpoint()
        LOGGER.info("All companies processed, checkpoint cleared")


async def scrape_single_company(
    page: Page,
    company_name: str,
    symbol: str,
    mouse_state: MouseState
):
    main_search_input = page.locator('[data-cy-id="search-search-field"]')
    await main_search_input.wait_for(timeout=10000)

    await human_move_and_click(page, '[data-cy-id="search-search-field"]', mouse_state)
    await random_pause(0.3, 0.7)

    await page.keyboard.press("Control+a")
    await page.keyboard.press("Backspace")

    await human_type(page, company_name)

    search_results_list = page.locator('[data-cy-id="search-results-list"]')
    await search_results_list.wait_for(timeout=10000)
    LOGGER.debug("raw search result: %s", search_results_list)
    await random_pause(0.6, 1.4)

    listing_found = await find_and_click_sgx_listing(
        page=page,
        results_list=search_results_list,
        mouse_state=mouse_state,
        symbol=symbol
    )

    if not listing_found:
        return

    await browse_company_page(page)
    await browse_detour_tabs(page, mouse_state)

    await human_move_and_click(page, 'a[data-cy-id="desktop-sidebar-nav-6"]', mouse_state)
    await page.wait_for_load_state("domcontentloaded", timeout=15000)
    await random_pause(2.0, 3.5)
    await human_scroll(page, scroll_distance=random.randint(100, 250))

    await page.reload(wait_until="domcontentloaded")
    await page.wait_for_selector('[data-cy-id="management-section"]', state="visible", timeout=15000)
    await read_management_page(page, mouse_state)

    await extract_data(page=page, company_name=company_name, symbol=symbol)


async def extract_data(
    page: Page,
    company_name: str,
    symbol: str
) -> None:
    management_page_html = await page.content()
    extracted_data = extract_management_and_ownership(management_page_html)

    safe_name = sanitize_filename(company_name)

    data_dir = Path('data')
    subdirectories = ["management", "shareholders"]

    for subdirectory_name in subdirectories:
        (data_dir / subdirectory_name).mkdir(parents=True, exist_ok=True)

    management_dir = data_dir / 'management'
    shareholders_by_type_dir = data_dir / 'shareholders/by_type'
    top_shareholders_dir = data_dir / 'shareholders/top_shareholders'

    filename_management = management_dir / f'{safe_name}_.json'
    filename_top_shareholders = top_shareholders_dir / f'{safe_name}_{symbol}.json'
    filename_shareholders_by_type = shareholders_by_type_dir / f'{safe_name}_{symbol}.json'

    management_payload = extracted_data['management']
    shareholders_by_type = extracted_data['ownership_by_type']
    top_shareholders = extracted_data['top_shareholders']

    top_shareholders_v2 = {
        "symbol": symbol,
        "items": top_shareholders
    }

    write_json(management_payload, filename_management)
    write_json(shareholders_by_type, filename_shareholders_by_type)
    write_json(top_shareholders_v2, filename_top_shareholders)

    LOGGER.info("Saved data for company: %s", company_name)


async def find_and_click_sgx_listing(
    page: Page,
    results_list,
    mouse_state: MouseState,
    symbol: str
) -> bool:
    all_result_links = results_list.locator("a")
    link_count = await all_result_links.count()

    for link_index in range(link_count):
        try:
            link = all_result_links.nth(link_index)
            ticker_element = link.locator("p").first
            ticker_text = await ticker_element.text_content()

            if ticker_text is None:
                continue

            ticker_text = ticker_text.strip()

            if ticker_text == f"SGX:{symbol}":
                await link.scroll_into_view_if_needed()
                await random_pause(0.5, 1.2)
                await human_move_and_click_locator(page, link, mouse_state)
                return True

            await random_pause(0.05, 0.15)

        except Exception:
            continue

    await page.keyboard.press("Escape")
    await random_pause(0.3, 0.7)
    return False


if __name__ == '__main__':
    account_collections = {
        'acc_one': {
            'email': "test@gmail.com",
            'pass': "test",
        },
    }

    acc_one = account_collections['acc_one']

    companies = [
        {'name': 'ESR-REIT', 'symbol': '9A4U'},
        {'name': 'Top Glove Corp Bhd', 'symbol': 'BVA'},
        {'name': 'Sinarmas Land Ltd', 'symbol': 'A26'},
        {'name': 'AEM Holdings Ltd', 'symbol': 'XWA'}
    ]

    asyncio.run(run_automation(
        email_address=acc_one['email'],
        account_password=acc_one['pass'],
        companies=companies,
        headless=False
    ))
