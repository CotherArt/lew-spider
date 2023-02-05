from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
import json
import keys
import random
from urllib import request
import os

perfils_file = 'perfiles.json'
images_path = 'images/'
PATH = "chromedirver.exe"

driver = webdriver.Chrome(PATH)
driver.implicitly_wait(10)

# download image from url
# Descarga una imagen de una cuenta de usuario y la guarda en su propia carpeta
def download_image(web_url, folder=images_path, img_name=None):  
    # create folder if do not exist
    os.makedirs(folder)
    
    # genera un nombre aleatorio para la imgaen, cunado no hay parametro img_name
    if img_name == None:
        name = random.randrange(1,100)  
        img_name = name;
        
    # genera la ruta completa de la imagen 
    fullname = folder +'/'+ str(img_name) +".jpg"
    
    # descarga la imagen de internet
    request.urlretrieve(web_url,fullname)
    
    print('+ '+fullname)

#Save the list of accounts to a file
def save_accounts_dict(accounts):
    if not len(accounts) == 0:
        with open("perfiles.json", "w") as fp:
            json.dump(accounts, fp, indent=4)

#Load the accounts from a file
def load_accounts_dict():
    accounts_dict = {}
    if perfils_file in os.listdir():
        with open("perfiles.json", "r") as fp:
            accounts_dict = json.load(fp)
    else:
        save_accounts_dict(accounts_dict)
        
    return accounts_dict

# go to account and scrape their images
def get_images_from(account):
    driver.get('https://twitter.com/' + account)

    # Open carrusel
    try:
        carrusel = driver.find_element(By.XPATH, '//div[@class="css-1dbjc4n r-1iusvr4 r-16y2uox r-a5pmau r-bnwqim"][1]')
        carrusel.click()
    except:
        print('Error. Carrusel not finded')
        return
    
    # clic on next
    try:
        for i in range(30):
            next = driver.find_element(By.XPATH, '//div[@aria-label="Next slide"]')
            sleep(0.4)
            next.click()
    except:
        print('Error clicking Next on carrusel')

    # get the images
    imgs = driver.find_elements(By.XPATH, '//li//img[@alt="Image"]')
    imgs = [i.get_attribute('src') for i in imgs]
    print(imgs)

    # returns a list of image urls
    return imgs

#Listar todos los nombres de perfiiles
def list_following(account):
    path = 'https://twitter.com/'+account+'/following'
    driver.get(path)
    sleep(5)
    following_list = []
    following_list = driver.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]//div[@class="css-1dbjc4n r-1awozwy r-18u37iz r-1wbh5a2"]')
    following_list = [i.text for i in following_list]
    
    print(following_list)
    print(len(following_list))
        
    return following_list

def login_twitter():
    # Login to twitter
    driver.get("https://www.twitter.com/login")

    #login
    #set user
    username = driver.find_element(By.XPATH, '//input[@name="text"]')
    username.send_keys(keys.USER)

    # Click on "Next"
    btn_next = driver.find_element(By.XPATH, '//div[@role="button"][2]')
    btn_next.click()

    #set password
    password = driver.find_element(By.NAME, 'password')
    password.send_keys(keys.PASS)

    #click on login
    submit = driver.find_element(By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]')
    submit.click()

    sleep(2)

def print_dict(dictionary):
    print(json.dumps(dictionary, sort_keys=True, indent=4))

def url_to_dict(dictionary, img_weburl, account):
    accout_names = list(dictionary.keys())
    if account in accout_names:
        # print('existe la cuentaa: ' + account)
        if img_weburl in dictionary[account]:
            # print(f'existe la url: {img_weburl}')
            pass
        else:
            # print(f'+ adding url {img_weburl}')
            dictionary[account].append(img_weburl)
    else:
        print(f'+ adding [{account}] to the dictionary')
        dictionary[account] = [img_weburl]

    return dictionary

# Busca las cuentas de perfils_list, les roba las imagenes y guarda info en un archivo
def attack(account:str):
    print(f'Attacking {account}...')
    
    image_url_list = get_images_from(account)
    if image_url_list == None:
        print('- Images not found')
        return
    
    for idx, web_url in enumerate(image_url_list):
        perfils_dict = load_accounts_dict()
        # comprueba si la imagen ya se ha bajado anteriormente
        if web_url in list(perfils_dict.keys()):
            print('- La imagen ya existe')
            break
        
        folder = images_path + account
        download_image(web_url, folder, idx)
        perfils_dict = url_to_dict(perfils_dict, web_url, account)
        
        save_accounts_dict(perfils_dict)
        
def attack_list(perfils_list:list):
    print(f'Attacking {account}...')
    
    for account in perfils_list:
        attack(account)

# RECORDATORIO - Para funciones como esta, que realizan una acción a cada uno
# de los elementos de esa lista. Crea una función que solo se lo haga a un elemento y 
# crea otra que reciba la lista y la itere