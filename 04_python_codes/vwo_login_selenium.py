import os
import random
import re
import string
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def generate_random_email(domain: str = "example.com") -> str:
    local = "user_" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    return f"{local}@{domain}"


def ensure_directory(path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def find_first_present(driver: webdriver.Chrome, selectors: list[str]) -> Optional[tuple[str, str]]:
    for selector in selectors:
        try:
            driver.find_element(By.CSS_SELECTOR, selector)
            return ("css", selector)
        except NoSuchElementException:
            continue
    return None


def main() -> None:
    screenshot_path = Path("c:/MCP_Agents/02_selenium_mcp/screenshots/vwo_login_result.png")
    ensure_directory(screenshot_path)

    options = webdriver.ChromeOptions()
    # Explicitly ensure non-headless for visibility
    # (By default Chrome opens with a UI; we avoid adding any --headless flags.)

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    wait = WebDriverWait(driver, 15)

    try:
        driver.get("http://app.vwo.com")

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
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:where(:is(:-internal-has-text('Sign in'), :-internal-has-text('Log in'), :-internal-has-text('Login')))",
            "button",
        ]

        # Find and fill email
        email_locator = find_first_present(driver, email_selectors)
        if not email_locator:
            raise RuntimeError("Email input not found")
        email_element = driver.find_element(By.CSS_SELECTOR, email_locator[1])
        email_element.clear()
        email_element.send_keys(generate_random_email())

        # Find and fill password
        password_locator = find_first_present(driver, password_selectors)
        if not password_locator:
            raise RuntimeError("Password input not found")
        password_element = driver.find_element(By.CSS_SELECTOR, password_locator[1])
        password_element.clear()
        password_element.send_keys("Pwd_" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12)))

        # Click submit
        submit_locator = find_first_present(driver, submit_selectors)
        if submit_locator:
            driver.find_element(By.CSS_SELECTOR, submit_locator[1]).click()
        else:
            password_element.send_keys(Keys.ENTER)

        # Wait for a likely error message to appear
        error_text: Optional[str] = None
        try:
            # Try ARIA role alert
            alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='alert']")))
            error_text = alert.text.strip()
        except TimeoutException:
            # Try common error keywords in text nodes
            try:
                # Broad text match using XPath contains with case-insensitive translate
                error_node = wait.until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//*[contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'invalid') or "
                            "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'incorrect') or "
                            "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'wrong') or "
                            "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'error') or "
                            "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'failed')]",
                        )
                    )
                )
                error_text = error_node.text.strip()
            except TimeoutException:
                error_text = None

        # Take screenshot
        driver.save_screenshot(str(screenshot_path))

        if error_text:
            print(f"Observed error message: {error_text}")
        else:
            print("No explicit error message detected within timeout.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
