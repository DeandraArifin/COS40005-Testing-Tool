from playwright.sync_api import sync_playwright

def analyze_page(url: str):
    console_errors = []
    page_errors = []
    failed_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on(
            "console",
            lambda message:
                console_errors.append(message.text)
                if message.type == "error"
                else None
        )

        page.on(
            "pageerror",
            lambda error:
                page_errors.append(str(error))
        )

        page.on(
            "requestfailed",
            lambda request:
                failed_requests.append(request.url)
        )

        response = page.goto(url)

        result = {
            "status_code": response.status if response else None,
            "console_errors": console_errors,
            "page_errors": page_errors,
            "failed_requests": failed_requests,
        }

        browser.close()

    return result