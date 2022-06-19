from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from getpass import getpass

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
    link = raw_input("\nYour Canvas course's 'Grades' page URL: ")
    email = raw_input("\nEnter your CruzID: ")
    password = getpass("Enter your Gold password: ")
    customWeights = raw_input("\nWill you be entering custom weights? (y/n): ")
    if (customWeights == 'y') or (customWeights == 'yes') or (customWeights == 'Y') or (customWeights == 'Yes'):
        print("\n     You will be prompted to enter custom weights once the page loads.")
    twoAuth = raw_input("\nChoose preferred 2FA (push, phone, pass): ")

    driver = webdriver.Firefox(executable_path='./geckodriver')
    driver.implicitly_wait(8)

    # Canvas
    driver.get(link)

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

    asgnList = []
    contextList = []
    scoreList = []
    avgScoreList = []
    posPointsList = []
    weightDict = {}
    customWeightDict = {}
    pointsDict = {}
    avgPointsDict = {}
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
        customWeightDict[str(context.get_attribute('innerHTML'))] = float(((percent.get_attribute('innerHTML')).split('%'))[0]) / 100
        pointsDict[str(context.get_attribute('innerHTML'))] = 0
        avgPointsDict[str(context.get_attribute('innerHTML'))] = 0
        avgDict[str(context.get_attribute('innerHTML'))] = 0
        realAvgDict[str(context.get_attribute('innerHTML'))] = 0
        userDict[str(context.get_attribute('innerHTML'))] = 0
        realUserDict[str(context.get_attribute('innerHTML'))] = 0

    breadcrumbs = driver.find_element(By.ID, 'breadcrumbs').find_elements(By.TAG_NAME, 'span')
    className = breadcrumbs[2].get_attribute('innerHTML')

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

            asgnList.append(title)
            contextList.append(context)
            # print(title)
            # print(context)
            
            # Find total possible points for each score
            pointsPossible = tr.find_element(By.CLASS_NAME, 'points_possible')
            pointsPos = pointsPossible.text
            posPointsList.append(float(pointsPos))
            # print("out of: ", float(pointsPos))

            # Find user's score
            gradeParent = tr.find_element(By.CLASS_NAME, 'grade')
            userGrade = gradeParent.get_attribute('innerHTML').split('</span>\n                  ')
            userGradeF = userGrade[-1].split('\n')[0]
            scoreList.append(float(userGradeF))
            # print("grade:", float(userGradeF))
            avgScoreList.append(float(avg))

            # Adds up total average points and total points possible and puts them in dictionaries
            for k in weightDict.keys():
                if k == context:
                    pointsDict[k] += float(pointsPos)
                    avgPointsDict[k] += float(pointsPos)
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
            if float(pointsDict[k]) == 0 or float(avgPointsDict[k]) == 0:
                continue
            realAvgDict[k] = (float(avgDict[k]) / float(pointsDict[k])) * 100 * customWeightDict[k]
            realUserDict[k] = (float(userDict[k]) / float(pointsDict[k])) * 100 * customWeightDict[k]
        if customWeights == 'n' or customWeights == 'no' or customWeights == 'N' or customWeights == 'No':
            if float(pointsDict[k]) == 0 or float(avgPointsDict[k]) == 0:
                continue
            realAvgDict[k] = (float(avgDict[k]) / float(pointsDict[k])) * 100 * weightDict[k]
            realUserDict[k] = (float(userDict[k]) / float(pointsDict[k])) * 100 * weightDict[k]
        avgGradeF += realAvgDict[k]
        userGradeF += realUserDict[k]
    clear()
    print("\n")
    print('\033[1m' + className.center(70))
    print '\033[0m'
    print("+----------------+--------------+------------------+-----------------+")
    print("|    Category    |    Weight    |    Your Score    |    Class Avg    |")
    print("+----------------+--------------+------------------+-----------------+")
           
    for key, value in userDict.items():
        if float(pointsDict[key]) == 0 or float(avgPointsDict[key]) == 0:
            continue
        print("| " + key[:14] + " "* (14 - len(key)) + " | " + str("{:.2f}".format(float(customWeightDict[key])*100))[:5] + "%      " + " | " + str("{:.2f}".format(float(value) / float(pointsDict[key]) * 100))[:5] + "%           " + "| " + str("{:.2f}".format(float(avgDict[key]) / float(pointsDict[key]) * 100))[:5] + "%          " + "|")
    
    print("+----------------+--------------+------------------+-----------------+")
    print("| Weighted       | 100.0%       | " + "{:.2f}".format(float(userGradeF)) + "%           " + "| " + "{:.2f}".format(float(avgGradeF)) + "%          " + "|")
    print("| Total          |              |                  |                 |")
    print("+----------------+--------------+------------------+-----------------+")


    while 1:    
        options = raw_input("\nType 'p' to print each individual grade\nType 's' to print stats again\nType 'a' to add a 'What If' score to your total grade\nType 'r' to remove a score from your total grade\nType 'q' to quit\n\n     ")
        if options == 'q':
            quitPrompt = raw_input("\n     Are you sure? (y/n)")
            if quitPrompt == 'y' or quitPrompt == 'Y':
                curses.wrapper(main)
                break;    
        elif options == 'p':
            clear()
            print("\n")
            print("+--------------------+--------------------+--------------------+--------------------+")
            print("|        Name        |        Type        |     Your Score     |     Avg. Score     |")
            print("+--------------------+--------------------+--------------------+--------------------+")
            for i in range(len(asgnList)):
                print("| " + str(asgnList[i])[:18] + " "*(18 - len(str(asgnList[i]))) + " | " + str(contextList[i])[:18] + " "*(19 - len(str(contextList[i]))) + "| "+ str("{:.2f}".format(float(scoreList[i])/float(posPointsList[i])*100))[:5] + "%             " + "| " + str("{:.3f}".format(float(avgScoreList[i])/float(posPointsList[i])*100))[:5] + "%             " + "|")
            print("+--------------------+--------------------+--------------------+--------------------+")
        elif options == 'a':
            newContext = raw_input("\nEnter category (case sensitive) (type 'q' to go back): ")
            if newContext == 'q':
                continue
            if newContext not in contextList:
                print("\n     Category not found")
                continue
            newScore = raw_input("Enter your score: ")
            newPosPoints = raw_input("Enter total possible points: ")
            asgnList.append("What If Assignment")
            contextList.append(newContext)
            scoreList.append(float(newScore))
            avgScoreList.append(0)
            posPointsList.append(float(newPosPoints))
            userDict[newContext] += float(newScore)
            pointsDict[newContext] += float(newPosPoints)
            print("\n     What If Assignment has been added and tables have been updated.\n     Enter 'p' or 's' to view updates.") 
        elif options == 'r':
            newAsgn = raw_input("\nEnter assignment name (case sensitive) (type 'q' to go back): ")
            if newAsgn == 'q':
                continue
            if newAsgn not in asgnList:
                print("\n     Assignment name not found")
                continue
            i = asgnList.index(newAsgn)
            score = scoreList[i]
            del avgScoreList[i]
            posPoints = posPointsList[i]
            userDict[contextList[i]] -= float(score)
            pointsDict[contextList[i]] -= float(posPoints)
            # del contextList[i]
            del scoreList[i]
            del posPointsList[i]
            asgnList.remove(newAsgn)

            print("\n     " + contextList[i] + " has been removed and tables have been updated.\n     Enter 'p' or 's' to view updates.")

            del contextList[i]

        elif options == 's':
            avgGradeF = 0
            userGradeF = 0
            for k in weightDict.keys():
                if (customWeights == 'y') or (customWeights == 'yes') or (customWeights == 'Y') or (customWeights == 'Yes'):
                    if float(pointsDict[k]) == 0 or float(avgPointsDict[k]) == 0:
                        continue
                    realAvgDict[k] = (float(avgDict[k]) / float(avgPointsDict[k])) * 100 * customWeightDict[k]
                    realUserDict[k] = (float(userDict[k]) / float(pointsDict[k])) * 100 * customWeightDict[k]
                if customWeights == 'n' or customWeights == 'no' or customWeights == 'N' or customWeights == 'No':
                    if float(pointsDict[k]) == 0 or float(avgPointsDict[k]) == 0:
                        continue
                    realAvgDict[k] = (float(avgDict[k]) / float(avgPointsDict[k])) * 100 * weightDict[k]
                    realUserDict[k] = (float(userDict[k]) / float(pointsDict[k])) * 100 * weightDict[k]
                avgGradeF += realAvgDict[k]
                userGradeF += realUserDict[k]
            clear()
            print("\n")
            print('\033[1m' + className.center(70))
            print '\033[0m'
            print("+----------------+--------------+------------------+-----------------+")
            print("|    Category    |    Weight    |    Your Score    |    Class Avg    |")
            print("+----------------+--------------+------------------+-----------------+")
            
            totalWeight = 0
            for key, value in customWeightDict.items():
                if float(pointsDict[key]) == 0 or float(avgPointsDict[key]) == 0:
                    continue
                totalWeight += float(value)

            for key, value in userDict.items():
                if float(pointsDict[key]) == 0 or float(avgPointsDict[key]) == 0:
                    continue
                print("| " + key[:14] + " "* (14 - len(key)) + " | " + str("{:.2f}".format(float(customWeightDict[key])*100))[:5] + "%      " + " | " + str("{:.2f}".format(float(value) / float(pointsDict[key]) * 100))[:5] + "%           " + "| " + str("{:.2f}".format(float(avgDict[key]) / float(avgPointsDict[key]) * 100))[:5] + "%          " + "|")
            
            print("+----------------+--------------+------------------+-----------------+")
            print("| Weighted       | " + ("{:.2f}".format(float(totalWeight)* 100))[:5] + "%       | " + "{:.2f}".format(float(userGradeF)/totalWeight) + "%           " + "| " + "{:.2f}".format(float(avgGradeF)/totalWeight) + "%          " + "|")
            print("| Total          |              |                  |                 |")
            print("+----------------+--------------+------------------+-----------------+")
        else:
            print("\n     Command not found")
            continue

    # while 1:
        # addScores = raw_input("\nWould you like to add any 'What If' assignments and recalculate your grade? (y/n): ")
        # if (addScores == 'y') or (addScores == 'yes') or (addScores == 'Y') or (addScores == 'Yes'):
        #     newCateg = raw_input("\n     Type assignment category (case sensitive): ")
        #     newPoints = raw_input("\n     Type total possible points: ")
        #     newScore = raw_input("\n     Type score earned: ")

            

        # else:
        #     curses.wrapper(main)
        #     break
    

# --------------- Curses code below ---------------
menu = ['Start', 'Exit']

# Print menu
def print_menu(stdscr, currentRow):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    for i, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + i
        if i == currentRow:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y,x-10,row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x-10, row)

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
            elif currentRow == len(menu)-2:
                stdscr.refresh()
                curses.endwin()
                avg()
                break

        print_menu(stdscr, currentRow)
        stdscr.refresh()

curses.wrapper(main)