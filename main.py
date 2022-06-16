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

    # Switch out of iframe
    driver.switch_to.default_content()
    driver.implicitly_wait(20)
    
    # Find grade weighting and put in dict
    weightDict = {}
    weightTable = driver.find_element(By.CLASS_NAME, 'summary')
    weightBody = weightTable.find_element(By.TAG_NAME, 'tbody')
    weightRow = weightBody.find_elements(By.TAG_NAME, 'th')
    weightRow2 = weightBody.find_elements(By.TAG_NAME, 'td')
    for context, percent in zip(weightRow, weightRow2):
        if str(context.get_attribute('innerHTML')) == 'Total':
            continue
        weightDict[str(context.get_attribute('innerHTML'))] = float(((percent.get_attribute('innerHTML')).split('%'))[0])
    print(weightDict)

    # Find each score details table
    tables = driver.find_elements(By.CLASS_NAME, 'score_details_table')
    driver.implicitly_wait(3)
    for table in tables:
        # Get class average score for assignment
        avg1 = table.find_element(By.TAG_NAME, 'td')
        avg2 = (avg1.get_attribute('innerHTML').split('\n                        '))[-1]
        avg = (avg2.split('\n'))[0]

        # Skip if table is comment not score table
        if '<span' in avg:
            continue
        print("avg: ", float(avg))
        driver.implicitly_wait(3)

        # Find user grade
        td= table.find_element_by_xpath("..")
        tr= td.find_element_by_xpath("..")
        tbody = tr.find_element_by_xpath("..")
        driver.implicitly_wait(3)

        scoreID = table.get_attribute('id')
        # There are edge cases where scoreID may be empty
        if scoreID:
            # Navigate to correct dir
            score = scoreID.split('score_details_')
            submissionID = 'submission_' + str(score[1])
            tr = tbody.find_element(By.ID, submissionID)

            # Grab assignment title and context (hw, quiz, final, etc.)
            titleEl = tr.find_element(By.TAG_NAME, 'a')
            title = titleEl.get_attribute("innerHTML")
            contextEl = tr.find_element(By.CLASS_NAME, 'context')
            context = contextEl.get_attribute("innerHTML")
            print(title)
            print(context)
            
            # Find total possible points for each score
            pointsPossible = tr.find_element(By.CLASS_NAME, 'points_possible')
            pointsPos = pointsPossible.text
            print("out of: ", float(pointsPos))

            # Find user's score
            gradeParent = tr.find_element(By.CLASS_NAME, 'grade')
            userGrade = gradeParent.get_attribute('innerHTML').split('</span>\n                  ')
            userGradeF = userGrade[-1].split('\n')[0]
            print("grade:", float(userGradeF))

        else: # Score ID empty
            continue
        print("-----------------\n")

main()

