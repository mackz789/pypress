import os, sys, shutil, urllib.request, zipfile, pymysql.cursors, configparser, random, string
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from warnings import filterwarnings
from tkinter import *
from tkinter.messagebox import showinfo

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '', 'config.ini'))

def ConfigSectionMap(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

options = ConfigSectionMap("Paths")
filepath = options['filepath']
URI = options['uri']
username = options['username']
email = options['email']

master = Tk()

e = Entry(master)
e.pack()

e.focus_set()

def callback():
    print (e.get())

b = Button(master, text="get", width=10, command=callback)
b.pack()

mainloop()


#clientfolder = input("Enter the name of the client folder: ")
clientfolder = clientfolder.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:,/<>?\|`~-=_+"})
clientfolder = clientfolder.lower()

#Creates Client Folder
newpath = filepath+clientfolder[0]+'/'+clientfolder
while os.path.exists(newpath):
    clientfolder = input("That folder already exists, please try another name: ")
    newpath = filepath+clientfolder[0]+'/'+clientfolder
os.makedirs(newpath)
print("Created new directory at "+newpath)

wpzipfile = newpath+'/'+"wordpress.zip"

#Downloads Wordpress
urllib.request.urlretrieve("https://wordpress.org/latest.zip", wpzipfile)
print("Downloaded Wordpress")

#Extract Wordpress Files
with zipfile.ZipFile(wpzipfile, "r") as z:
    z.extractall(newpath+'/')
print("Extracted Wordpress files")

#Deletes Wordpress.zip
os.remove(wpzipfile)
print("Deleted old wordpress.zip")

#Moves files from wordpress folder into original client folder
for filename in os.listdir(newpath+'/wordpress'):
    target = os.path.join(newpath, filename)
    shutil.move(os.path.join(newpath+'/wordpress', filename), target)

shutil.rmtree(newpath+'/wordpress')
print("Moved files out of Wordpress folder")

#Create Database
filterwarnings("ignore", category = pymysql.Warning)

db_connection = pymysql.connect(host='localhost', user='root', passwd='')
cursor = db_connection.cursor()
dbname = clientfolder
dbcreated = cursor.execute('CREATE DATABASE IF NOT EXISTS '+clientfolder)
while dbcreated != 1:
    dbname = clientfolder+str(random.randint(1, 99))
    dbcreated = cursor.execute('CREATE DATABASE IF NOT EXISTS '+dbname)
print("Created new database: "+dbname)

#Fill out Database Form
browser = webdriver.Firefox()
browser.get(URI+clientfolder[0]+'/'+clientfolder)
linkElem = browser.find_element_by_class_name('button')
type(linkElem)
linkElem.click()
dbnameElem = browser.find_element_by_id('dbname').clear()
dbnameElem = browser.find_element_by_id('dbname')
dbnameElem.send_keys(clientfolder)
unameElem = browser.find_element_by_id('uname').clear()
unameElem = browser.find_element_by_id('uname')
unameElem.send_keys('root')
passwordElem = browser.find_element_by_id('pwd').clear()
passwordElem = browser.find_element_by_id('pwd')
passwordElem.submit()

#Create wp-config.php
configElem = browser.find_element_by_id('wp-config').get_attribute('value')
configElem += """/*FTP Addition*/
define('FTP_HOST', 'localhost');
define('FTP_USER', 'daemon');
define('FTP_PASS', 'xampp');

if(is_admin()) {
add_filter('filesystem_method', create_function('$a', 'return "direct";' ));
define( 'FS_CHMOD_DIR', 0751 );
}

define('FS_METHOD','direct');"""
with open(newpath+'/'+'wp-config.php', 'w') as config:
    config.write(configElem)
print("Created wp-config.php")

#Run the Install
installElem = browser.find_element_by_link_text("Run the install")
type(installElem)
installElem.click()
print("Ran the install")

#Create Site Title and Username and login
siteElem = browser.find_element_by_id('weblog_title')
siteElem.send_keys(clientfolder)
usernameElem = browser.find_element_by_id('user_login')
usernameElem.send_keys(username)
sitepwdElem = browser.find_element_by_id('pass1-text').get_attribute('value')
print("Your password is "+sitepwdElem)
with open(newpath+'/'+'password.txt', 'w') as password:
    password.write('Username: '+username+'\n')
    password.write('Password '+sitepwdElem+'\n')
    password.write('Database: '+dbname)
emailElem = browser.find_element_by_id('admin_email')
emailElem.send_keys(email)
emailElem.submit()
loginElem = browser.find_element_by_link_text("Log In")
type(loginElem)
loginElem.click()
usernameElem = browser.find_element_by_id('user_login')
usernameElem.send_keys(username)
passwordElem = browser.find_element_by_id('user_pass')
passwordElem.send_keys(sitepwdElem)
passwordElem.submit()
print("Created Site Title and User and logged into site")

print("You may now build your Wordpress site")