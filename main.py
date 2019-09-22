import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import smtplib


# Python code to illustrate Sending mail with attachments
# from your Gmail account

# libraries to be imported
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def sendEmail(toaddr, jobTitle):
    yourName = "John"
    fromaddr = "you@emaildomain.com"
    password = "paSsWoRd1234"
    CVfilename = "cv.pdf"
    mailSubject = "Application for " + jobTitle
    body = """
    Hello

    My name is {} and I am applying to the position of {}.
    I have attached my CV to this mail.

    Thank you
    """.format(
        yourName, jobTitle
    )

    msg = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = mailSubject
    body = "Body_of_the_mail"
    msg.attach(MIMEText(body, "plain"))
    attachment = open(CVfilename, "rb")
    p = MIMEBase("application", "octet-stream")
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "attachment; filename= %s" % CVfilename)
    msg.attach(p)
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()
    return True


def findEmailInText(text):
    rgx = r"(?:\.?)([\w\-_+#~!$&\'\.]+(?<!\.)(@|[ ]?\(?[ ]?(at|AT)[ ]?\)?[ ]?)(?<!\.)[\w]+[\w\-\.]*\.[a-zA-Z-]{2,3})(?:[^\w])"
    matches = re.findall(rgx, text)
    get_first_group = lambda y: list(map(lambda x: x[0], y))
    emails = get_first_group(matches)
    return emails


def getHtmlTextWithSelenium(url):
    driver = webdriver.Chrome("chromedriver")
    driver.get(url)
    pageSource = driver.page_source
    driver.quit()
    return pageSource


def scrapeByPageNumber(currentpage):

    mainJobUrl = "https://www.itjobs.pt"
    mainUrl = "https://www.itjobs.pt/emprego?page="

    currentMainUrl = mainUrl + str(currentPage)

    currentPageHtml = requests.get(currentMainUrl).text

    soup = BeautifulSoup(currentPageHtml, "html.parser")

    jobColumns = soup.find_all("ul", {"class": "list-unstyled listing"})

    allJobPageUrls = []

    for col in jobColumns:
        xs = col.find_all("a", {"class": "title"})
        allJobPageUrls += [[x["href"], x["title"]] for x in xs]

    for i in allJobPageUrls:
        thisJobUrl = mainJobUrl + i[0]
        thisJobTitle = i[1]
        jobPageHtml = getHtmlTextWithSelenium(thisJobUrl)
        soup = BeautifulSoup(jobPageHtml, "html.parser")
        jobDescription = soup.find_all("div", {"class": "content-block"})[0].text
        print(thisJobTitle)
        emailsFound = findEmailInText(jobDescription)
        if len(emailsFound) > 0:
            print("Found email {} , sending email...".format(emailsFound[0]))
            sendEmail(emailsFound[0], thisJobTitle)
            print("Email sent!")
        else:
            print("Email not found!")
        print("\n\n")


if __name__ == "__main__":
    print(
        "Plase go to sendEmail function and change the variables according to your preference"
    )
    currentPage = 1
    while True:
        scrapeByPageNumber(currentPage)
        currentPage += 1
