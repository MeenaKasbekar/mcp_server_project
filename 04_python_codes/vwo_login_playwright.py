import re
import string
import random
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def generate_random_email(domain: str = "example.com") -> str:
    local = "user_" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    return f"{local}@{domain}"


def ensure_dir(path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def fill_login(page, email_value: str, password_value: str) -> None:
    email_selectors = [
        "input[type='email']",
        "input[name*='email' i]",
        "input[id*='email' i]",
        "input[placeholder*='email' i]",
    ]
    password_selectors = [
        "input[type='password']",
        "input[name*='pass' i]",
        "input[id*='pass' i]",
        "input[placeholder*='password' i]",
    ]

    email_input = None
    for s in email_selectors:
        loc = page.locator(s).first
        if loc.count() > 0:
            email_input = loc
            break
    if email_input is None:
        try:
            email_input = page.get_by_label(re.compile("email", re.I))
        except Exception:
            pass
    if email_input is None:
        raise RuntimeError("Email input not found")

    password_input = None
    for s in password_selectors:
        loc = page.locator(s).first
        if loc.count() > 0:
            password_input = loc
            break
    if password_input is None:
        try:
            password_input = page.get_by_label(re.compile("password", re.I))
        except Exception:
            pass
    if password_input is None:
        raise RuntimeError("Password input not found")

    email_input.fill(email_value)
    password_input.fill(password_value)

    for s in [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Sign in')",
        "button:has-text('Log in')",
        "button:has-text('Login')",
    ]:
        if page.locator(s).count() > 0:
            page.locator(s).first.click()
            return
    password_input.press("Enter")


def wait_for_error(page, timeout_ms: int = 10000) -> Optional[str]:
    try:
        alert = page.get_by_role("alert")
        alert.wait_for(state="visible", timeout=timeout_ms)
        return alert.inner_text().strip()
    except Exception:
        pass
    try:
        generic = page.locator("text=/invalid|incorrect|wrong|error|failed/i").first
        generic.wait_for(state="visible", timeout=timeout_ms)
        return generic.inner_text().strip()
    except Exception:
        return None


def run() -> None:
    screenshot = Path("c:/MCP_Agents/01_playwrite_mcp/screenshots/vwo_login_result.png")
    ensure_dir(screenshot)

    email = generate_random_email()
    password = "Pwd_" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://app.vwo.com", wait_until="domcontentloaded")
        fill_login(page, email, password)

        try:
            error_text = wait_for_error(page, timeout_ms=10000)
        except PlaywrightTimeoutError:
            error_text = None

        page.screenshot(path=str(screenshot), full_page=True)

        context.close()
        browser.close()

    if error_text:
        print(f"Observed error message: {error_text}")
    else:
        print("No explicit error message detected within timeout.")


if __name__ == "__main__":
    run()
