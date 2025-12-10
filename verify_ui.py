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
            header_el.screenshot(path="verification_header.png")
        else:
            print("Header not found!")

        # 4. Open a Modal
        print("Opening modal for first item...")
        # Click the first 'View Details' button
        first_btn = page.locator(".details-btn").first
        first_btn.click()

        # Wait for modal
        page.wait_for_selector(".modal-content")
        page.wait_for_timeout(500) # Animation

        # Screenshot Modal
        print("Screenshotting Modal...")
        page.screenshot(path="verification_modal.png")

        browser.close()

if __name__ == "__main__":
    verify_changes()
