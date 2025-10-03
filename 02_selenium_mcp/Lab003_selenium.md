Python and Java Selenium examples for opening `http://app.vwo.com`, filling random credentials, submitting, waiting for an error message, taking a screenshot, and closing the browser (non-headless).

Run prerequisites
- Python: `pip install selenium`
- Java: Ensure Selenium dependencies are available (e.g., via Maven/Gradle) and ChromeDriver managed by Selenium Manager (Selenium 4.6+), or put `chromedriver` on PATH.

Python (run)
```bash
python c:\MCP_Agents\02_selenium_mcp\vwo_login_selenium.py
```

Java (compile & run, assuming classpath configured for Selenium)
```bash
javac c:\MCP_Agents\02_selenium_mcp\VwoLoginSelenium.java
java -cp .;path\to\selenium\libs\* -Dwebdriver.chrome.driver=chromedriver VwoLoginSelenium
```

Screenshots are saved to:
- Python: `c:\MCP_Agents\02_selenium_mcp\screenshots\vwo_login_result.png`
- Java: `c:\MCP_Agents\02_selenium_mcp\screenshots\vwo_login_result_java.png`

can you open the http://app.vwo.com , make the headless false and add a random email, password in the text box and click on the submit button and verify the message of error after sometime using the selenium mcp and take screenshot and give me python and java code also.