import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.List;
import java.util.Locale;
import java.util.NoSuchElementException;
import java.util.Random;
import java.util.concurrent.TimeoutException;

import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.io.FileHandler;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class VwoLoginSelenium {

    private static String randomEmail() {
        String chars = "abcdefghijklmnopqrstuvwxyz0123456789";
        StringBuilder sb = new StringBuilder("user_");
        Random r = new Random();
        for (int i = 0; i < 10; i++) sb.append(chars.charAt(r.nextInt(chars.length())));
        return sb.append("@example.com").toString();
    }

    private static void ensureDirectory(Path filePath) throws IOException {
        Path parent = filePath.getParent();
        if (parent != null && !Files.exists(parent)) {
            Files.createDirectories(parent);
        }
    }

    private static WebElement firstPresent(WebDriver driver, List<By> bys) {
        for (By by : bys) {
            try {
                WebElement el = driver.findElement(by);
                if (el != null) return el;
            } catch (NoSuchElementException ignored) {}
        }
        return null;
    }

    public static void main(String[] args) throws IOException {
        Path screenshot = Paths.get("c:/MCP_Agents/02_selenium_mcp/screenshots/vwo_login_result_java.png");
        ensureDirectory(screenshot);

        ChromeOptions options = new ChromeOptions();
        // Non-headless by default
        WebDriver driver = new ChromeDriver(options);
        driver.manage().window().maximize();

        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

        try {
            driver.get("http://app.vwo.com");

            WebElement email = firstPresent(driver, List.of(
                By.cssSelector("input[type='email']"),
                By.cssSelector("input[name*='email' i]"),
                By.cssSelector("input[id*='email' i]"),
                By.cssSelector("input[placeholder*='email' i]")
            ));
            if (email == null) throw new RuntimeException("Email input not found");
            email.clear();
            email.sendKeys(randomEmail());

            WebElement password = firstPresent(driver, List.of(
                By.cssSelector("input[type='password']"),
                By.cssSelector("input[name*='pass' i]"),
                By.cssSelector("input[id*='pass' i]"),
                By.cssSelector("input[placeholder*='password' i]")
            ));
            if (password == null) throw new RuntimeException("Password input not found");
            password.clear();
            password.sendKeys("Pwd_" + java.util.UUID.randomUUID());

            WebElement submit = firstPresent(driver, List.of(
                By.cssSelector("button[type='submit']"),
                By.cssSelector("input[type='submit']"),
                By.cssSelector("button")
            ));
            if (submit != null) submit.click(); else password.sendKeys(Keys.ENTER);

            String errorText = null;
            try {
                WebElement alert = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[role='alert']")));
                errorText = alert.getText().trim();
            } catch (TimeoutException ex) {
                try {
                    WebElement generic = wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath(
                        "//*[contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'invalid') or " +
                        "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'incorrect') or " +
                        "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'wrong') or " +
                        "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'error') or " +
                        "contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'failed')]"
                    )));
                    errorText = generic.getText().trim();
                } catch (TimeoutException ignored) {}
            }

            File src = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            FileHandler.copy(src, screenshot.toFile());

            if (errorText != null && !errorText.isEmpty()) {
                System.out.println("Observed error message: " + errorText);
            } else {
                System.out.println("No explicit error message detected within timeout.");
            }

        } finally {
            driver.quit();
        }
    }
}
