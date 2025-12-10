from playwright.sync_api import sync_playwright

def verify_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Load the page
        print("Navigating to page...")
        page.goto("http://localhost:8080/vaquero-discounts.html")

        # 2. Wait for data to load
        print("Waiting for grid...")
        page.wait_for_selector(".grid")

        # 3. Screenshot Header
        print("Screenshotting Header...")
        header_el = page.locator(".utrgv-header")
        if header_el.count() > 0:
            header_el.screenshot(path="verification_header_logo.png")
        else:
            print("Header not found!")

        # 4. Screenshot App Header with Buttons
        print("Screenshotting App Header...")
        app_header_el = page.locator(".app-header")
        if app_header_el.count() > 0:
            app_header_el.screenshot(path="verification_app_header.png")
        else:
            print("App Header not found!")

        browser.close()

if __name__ == "__main__":
    verify_changes()
