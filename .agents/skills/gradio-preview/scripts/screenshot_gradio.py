"""Headless screenshot of the BJJ-VQA Gradio leaderboard app."""  # noqa: INP001

import sys

from playwright.sync_api import sync_playwright

from app.app import main as create_app

PORT = 7860


def main() -> None:
    """Launch Gradio, take a headless screenshot, and exit."""
    output = sys.argv[1] if len(sys.argv) > 1 else "screenshot.png"

    app = create_app()
    app.launch(prevent_thread_lock=True, server_port=PORT, quiet=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                base_url=f"http://127.0.0.1:{PORT}",
            )
            page = context.new_page()
            page.goto("/", wait_until="domcontentloaded", timeout=30000)
            # Wait for Gradio app to initialize
            page.wait_for_timeout(5000)
            page.screenshot(path=output, full_page=True)
            context.close()
            browser.close()
    finally:
        app.close()

    print(f"Screenshot saved to {output}")  # noqa: T201


if __name__ == "__main__":
    main()
