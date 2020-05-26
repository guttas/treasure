
# coding: utf-8

# In[8]:


from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from git import Repo
import logging

import time
import os, sys

def openChrome():
    driver = None
    try:
        #setup options
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        option.add_argument('disable-infobars')
        #open chrome
        driver = webdriver.Chrome(chrome_options=option)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        logging.info("openChrome Exception: " + str(e))

    return driver

def getCommitSHA():
    repo = Repo("D:\\Disk1\\Git\\altreps")
    for remote in repo.remotes:
        print(remote)
        fetch = remote.fetch()

    commit = repo.commit('origin/dev/senna/altreps')
    print(commit)
    logging.info("Origin SHA: " + commit.hexsha)

    return commit.hexsha

def operationAuth(driver, branchname, email, commitSHA):
    url = "http://invci.ecs.ads.autodesk.com/#/git_ondemand/input"
    #branchname = "dev/senna/altreps"
    #email = "tao.guo@autodesk.com"
    lastcommitfile = os.path.dirname(os.path.abspath(__file__)) + '\\' + branchname.replace('/', '_') + '.txt'
    print(lastcommitfile)

    try:
        lastcommit = ''
        if os.path.exists(lastcommitfile):
            with open(lastcommitfile, 'r') as file:
                lastcommit = file.read()
                print(lastcommit)

        logging.info("Last commit SHA: " + lastcommit)

        #open url
        driver.get(url)
        time.sleep(1)

        behaviorEle = driver.find_element_by_xpath("//*[@name='behavior']")
        behavior = Select(behaviorEle)
        behavior.select_by_index(0) # build
        time.sleep(1)

        config = driver.find_element_by_xpath("//*[@name='config']")
        Select(config).select_by_index(2) # debug & release
        time.sleep(1)

        branch = driver.find_element_by_xpath("//*[@name='branch']")
        branch.send_keys(branchname)
        time.sleep(1)

        commit = driver.find_element_by_xpath("//*[@name='commit']")
        commit.send_keys(commitSHA)

        make_setups = driver.find_element_by_xpath("//*[@name='make_setups']")
        if make_setups.is_selected():
            make_setups.click()

        if commitSHA != lastcommit:

            driver.find_element_by_xpath("//*[@name='email_to']").clear()
            driver.find_element_by_xpath("//*[@name='email_to']").send_keys(email)
            time.sleep(1)

            # submit
            driver.find_element_by_xpath("//*[@type='submit']").click()
            time.sleep(1)

            with open(lastcommitfile, 'w') as file:
                file.write(commitSHA)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        logging.info("operationAuth Exception: " + str(e))
    finally:
        driver.quit()

def main(args):
    logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__)) + '\\' +'log.txt',
    level=logging.INFO,
    format= '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    driver = openChrome()
    if driver:
        operationAuth(driver, args[0], args[1], getCommitSHA())
    else:
        logging.info("Chrome is not started properly.")

if __name__ == '__main__':
    main(sys.argv[1:])


