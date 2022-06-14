from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from getpass import getpass
from bs4 import BeautifulSoup

def main():
    # Login input
    email = raw_input("Enter your CruzID: ")
    password = getpass("Enter your Gold Password: ")

    # Setup webdriver
    driver = webdriver.Firefox(executable_path='./geckodriver')
    driver.implicitly_wait(8)

    # Canvas
    driver.get('https://canvas.ucsc.edu/courses/52588/grades')

    # Send username
    emailBox = driver.find_element(By.ID, "username")
    emailBox.send_keys(email)

    # Send password
    passwordBox = driver.find_element(By.ID, "password")
    passwordBox.send_keys(password)

    # Click login button
    loginButton = driver.find_element(By.NAME, "_eventId_proceed")
    loginButton.click()

    # Switch contexts to two auth iframe
    iframe = driver.find_element_by_xpath("//iframe[@id='duo_iframe']")
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(10)

    # Click 'Call Me' button
    phoneDiv = driver.find_element(By.CLASS_NAME, "phone-label")
    WebDriverWait(phoneDiv, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "button"))).click()

    driver.switch_to.default_content()
    driver.implicitly_wait(10)
    
    tables = driver.find_elements(By.CLASS_NAME, 'score_details_table')
    for table in tables:
        avg = table.find_element(By.TAG_NAME, 'td')
        driver.implicitly_wait(3)
        print(avg.get_attribute('innerHTML'))
    # driver.implicitly_wait(5)
    # for table in tables:
    #     tbody = table.find_element(By.TAG_NAME, 'tbody')
    #     tr = list(tbody.find_elements(By.TAG_NAME, 'td'))
    #     driver.implicitly_wait(5)

    #     print(tr[0].text)

main()

