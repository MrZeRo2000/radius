
import os
import logging
import datetime

import click
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def setup_logger() -> logging.Logger:
    log_path = os.path.join(os.path.dirname(__file__), "../log/")
    log_file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path + log_file_name),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("main")


logger = setup_logger()

CLICK_LOGIN_TEXT = "Click here to log back in"


@click.command()
@click.option('--chrome_driver_path', prompt='Path to Chrome Driver', required=True)
@click.option('--url', prompt='Initial URL', required=True)
@click.option('--user_name', prompt='User Name', required=True)
@click.option('--password', prompt='Password', required=True)
def run(chrome_driver_path, url, user_name, password):

    os.environ['PATH'] = f"{os.environ['PATH']};{chrome_driver_path}"

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')

    driver = webdriver.Chrome(options=options)

    try:
        driver.implicitly_wait(10)
        driver.get(url)

        logout_elements = driver.find_elements(By.LINK_TEXT, "Logout")

        if len(logout_elements) == 1:
            logger.info("Found logout elements")
            logout_element = logout_elements[0]

            logger.info("Clicking logout")
            logout_element.click()

            logger.info("Waiting until login appears")
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.LINK_TEXT, CLICK_LOGIN_TEXT)))

            logger.info("Login appeared or timed out")
        else:
            logger.info("No logout elements")

        click_login_elements = driver.find_elements(By.PARTIAL_LINK_TEXT, "Click here to log")

        if len(click_login_elements) == 1:
            logger.info("Found login elements")
            click_login_element = click_login_elements[0]

            logger.info("Clicking login")
            click_login_element.click()

            logger.info("Waiting until switched to auth URL")
            wait_auth = WebDriverWait(driver, 10)
            wait_auth.until(EC.url_contains("auth"))

            logger.info("Switched to auth URL")

            driver.switch_to.frame("authFrm")

            logger.info("Switched to auth Frame")

            user_name_element = driver.find_elements(By.NAME, "userName")[0]
            password_element = driver.find_elements(By.NAME, "pwd")[0]
            submit_element = driver.find_elements(By.XPATH, "//input[@type='submit']")[0]

            logger.info("Logging in with given user name and password")

            user_name_element.send_keys(user_name)
            password_element.send_keys(password)
            submit_element.click()

            logger.info("Waiting for log in")

            wait_login = WebDriverWait(driver, 10)
            login_result = wait_login.until(EC.url_contains("loginDone  "))

            logger.info(f"Login result: {login_result}")

            pass
        else:
            logger.info("No login elements")

        pass

    except Exception as e:
        logger.error(str(e))
        raise e

    finally:
        driver.quit()


if __name__ == '__main__':
    run()
