from selenium import webdriver
from selenium.webdriver.common.by import By
from getpass import getpass
from bs4 import BeautifulSoup

def main():
    # Login input
    email = raw_input("Enter your CruzID: ")
    password = getpass("Enter your Gold Password: ")

    # Setup webdriver
    driver = webdriver.Firefox(executable_path='./geckodriver')
    driver.implicitly_wait(10)

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

    # Wait for two auth to load
    driver.implicitly_wait(10)

    phoneButton = driver.find_element(By.CLASS_NAME, "row-label phone-label")

main()