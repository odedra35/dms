import time

from selenium.common import NoSuchElementException

from logs import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = "http://localhost:8080"
driver = webdriver.Chrome()


def test_register() -> tuple[bool, str]:
    """Try to register new user.

        incase user already exists - pass
        incase user fails to register - fail
    """
    register_url = f"{url}/register"
    user, password, timeout = "testUser", "testUserPass", 10
    try:
        driver.get(register_url)
        f_user_name = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        f_password = driver.find_element(By.ID, "password")
        f_password_confirm = driver.find_element(By.ID, "confirm_password")

        # consider clear() the text field before filling it

        f_user_name.send_keys(user)
        f_password.send_keys(password)
        f_password_confirm.send_keys(password)

        driver.find_element(By.ID, "regSubmit").submit()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "logSubmit")))

    except NoSuchElementException as e:
        logger.error(e)
        return False, f"Could not locate id inside register form.\n{e}"
    except Exception as e:
        logger.error(e)
        return False, str(e)
    finally:
        driver.quit()

    return True, ""


def test_login():
    pass


def main():
    # ---------------------------------------------------------------------
    logger.info("Testing Register User: 'testUser', Password: 'testUserPass']")
    result, answer = test_register()
    if not result:
        logger.error(f"Register user test failed. \n{answer}\n")
        raise RuntimeError(f"Register user test failed. \n{answer}\n")
    logger.info("Register User test passed.")

    # ---------------------------------------------------------------------
    # result, answer = test_login()
    # if not result:
    #     logger.error(f"Login user test failed. \n{answer}\n")
    #     raise RuntimeError(f"Login user test failed. \n{answer}\n")
    # logger.info("Login User test passed.")


if __name__ == "__main__":
    main()