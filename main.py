from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from getpass import getpass
from bs4 import BeautifulSoup

import time
import curses

from os import system, name

# Clears command line
def clear(): 
    if name == 'nt': 
        x = system('cls') 
    else: 
        x = system('clear') 

# Function to calculate class average stats
def avg():
    clear()
    # Login input
    email = raw_input("\nEnter your CruzID: ")
    password = getpass("Enter your Gold password: ")
    customWeights = raw_input("\nWill you be entering custom weights? (y/n): ")
    if (customWeights == 'y') or (customWeights == 'yes') or (customWeights == 'Y') or (customWeights == 'Yes'):
        print("\n     You will be prompted to enter custom weights once the page loads.")
    twoAuth = raw_input("\nChoose preferred 2FA (push, phone, pass): ")

    driver = webdriver.Firefox(executable_path='./geckodriver')
    driver.implicitly_wait(8)

    # Canvas
    driver.get('https://canvas.ucsc.edu/courses/52596/grades')

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
    if twoAuth == 'phone':
        phoneDiv = driver.find_element(By.CLASS_NAME, "phone-label")
        WebDriverWait(phoneDiv, 200).until(EC.element_to_be_clickable((By.TAG_NAME, "button"))).click()
    # Click 'Push' button
    if twoAuth == 'push':
        pushDiv = driver.find_element(By.CLASS_NAME, "push-label")
        WebDriverWait(pushDiv, 200).until(EC.element_to_be_clickable((By.TAG_NAME, "button"))).click()
    # For password 2FA, user must push the button manually.

    # Switch out of iframe
    driver.switch_to.default_content()
    driver.implicitly_wait(2000)
    
    # Find grade weighting and put in dict. Also initialize total points possible, average points, and final average dictionaries. 
    # weightsDict - Weights of each category with respective values in 0.XX format.
    # pointsDict - Total possible points of each category with respective values in 0.XX format.
    # avgDict - Average points of each category with respective values in 0.XX format.
    # realAvgDict - Final calculated average of each respective category. All category values added up divided by 100 equals the final class average.
    
    weightDict = {}
    customWeightDict = {}
    pointsDict = {}
    avgDict = {}
    realAvgDict = {}
    userDict = {}
    realUserDict = {}
    weightTable = driver.find_element(By.CLASS_NAME, 'summary')
    weightBody = weightTable.find_element(By.TAG_NAME, 'tbody')
    weightRow = weightBody.find_elements(By.TAG_NAME, 'th')
    weightRow2 = weightBody.find_elements(By.TAG_NAME, 'td')
    clear()
    for context, percent in zip(weightRow, weightRow2):
        if str(context.get_attribute('innerHTML')) == 'Total':
            continue
        if (customWeights == 'y') or (customWeights == 'yes') or (customWeights == 'Y') or (customWeights == 'Yes'):
            customWeight = raw_input("Enter custom weight for '" + str(context.get_attribute('innerHTML')) + "' category (eg. type 40 if 40%): ")
            customWeightDict[str(context.get_attribute('innerHTML'))] = float(customWeight)  / 100
        weightDict[str(context.get_attribute('innerHTML'))] = float(((percent.get_attribute('innerHTML')).split('%'))[0]) / 100
        pointsDict[str(context.get_attribute('innerHTML'))] = 0
        avgDict[str(context.get_attribute('innerHTML'))] = 0
        realAvgDict[str(context.get_attribute('innerHTML'))] = 0
        userDict[str(context.get_attribute('innerHTML'))] = 0
        realUserDict[str(context.get_attribute('innerHTML'))] = 0

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
            # print(title)
            # print(context)
            
            # Find total possible points for each score
            pointsPossible = tr.find_element(By.CLASS_NAME, 'points_possible')
            pointsPos = pointsPossible.text
            # print("out of: ", float(pointsPos))

            # Find user's score
            gradeParent = tr.find_element(By.CLASS_NAME, 'grade')
            userGrade = gradeParent.get_attribute('innerHTML').split('</span>\n                  ')
            userGradeF = userGrade[-1].split('\n')[0]
            # print("grade:", float(userGradeF))

            # Adds up total average points and total points possible and puts them in dictionaries
            for k in weightDict.keys():
                if k == context:
                    pointsDict[k] += float(pointsPos)
                    avgDict[k] += float(avg)
                    userDict[k] += float(userGradeF)

        else: # Score ID empty
            continue
    
    # Calculate the average class score using total average scores and total points possible for each grade category. 
    # The total avg percentage for each category is then multiplied by the respective weights.
    avgGradeF = 0
    userGradeF = 0
    for k in weightDict.keys():
        if (customWeights == 'y') or (customWeights == 'yes') or (customWeights == 'Y') or (customWeights == 'Yes'):
            realAvgDict[k] = (float(avgDict[k]) / float(pointsDict[k])) * 100 * customWeightDict[k]
            realUserDict[k] = (float(userDict[k]) / float(pointsDict[k])) * 100 * customWeightDict[k]
        if customWeights == 'n' or customWeights == 'no' or customWeights == 'N' or customWeights == 'No':
            realAvgDict[k] = (float(avgDict[k]) / float(pointsDict[k])) * 100 * weightDict[k]
            realUserDict[k] = (float(userDict[k]) / float(pointsDict[k])) * 100 * weightDict[k]
        avgGradeF += realAvgDict[k]
        userGradeF += realUserDict[k]
    clear()
    print("==============================================")
    print("===== Average class grade Vs. Your grade =====")
    print("==============================================")
    print("\nCurrent average class grade (without counting any extra credit) is " + str(avgGradeF))
    print("Your current grade (without counting any extra credit) is " + str(userGradeF))
    print("\n")

# --------------- Curses code below ---------------
menu = ['Class Average', 'Calculate Score', 'Exit']

# Print menu
def print_menu(stdscr, currentRow):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    for i, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + i
        if i == currentRow:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y,x,row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)

    stdscr.refresh()

# Main menu
def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    currentRow = 0;

    print_menu(stdscr, currentRow)

    while 1:
        key = stdscr.getch()
        stdscr.clear()

        if key == curses.KEY_UP and currentRow > 0:
            currentRow -= 1
        elif key == curses.KEY_DOWN and currentRow < len(menu) - 1:
            currentRow += 1
        elif key == curses.KEY_ENTER or key in [10,13]:
            # If exit chosen
            if currentRow == len(menu)-1:
                break
            # If class average chosen
            elif currentRow == len(menu)-3:
                stdscr.refresh()
                curses.endwin()
                avg()
                break

        print_menu(stdscr, currentRow)
        stdscr.refresh()

curses.wrapper(main)