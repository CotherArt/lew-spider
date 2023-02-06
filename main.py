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

verbose = False
perfils_file = 'perfiles.json'
images_path = 'images/'
PATH = "chromedirver.exe"
max_images = 10  # cantidad de imagenes que se descargan


driver = webdriver.Chrome(PATH)
driver.implicitly_wait(10)

# descarga una imagen de internet
# Descarga una imagen de una cuenta de usuario y la guarda en su propia carpeta


def download_image(web_url, folder=images_path, img_name=None):
    log(f'Downloading {web_url} to {folder}')
    # create folder if do not exist
    os.makedirs(folder, exist_ok=True)

    # genera un nombre aleatorio para la imgaen, cunado no hay parametro img_name
    if img_name == None:
        name = random.randrange(1, 100)
        img_name = name
        
    # control de colision de nombres de  archivos ---------------------
    while image_exist(folder, img_name):
        if type(img_name) == int:
            new_image_name = img_name + 1
        else:
            new_image_name = f'{img_name}b'
        img_name = new_image_name
    
    # genera la ruta completa de la imagen
    fullname = f'{folder}/{img_name}.png'

    # descarga la imagen de internet
    request.urlretrieve(web_url, fullname)

    print('+ '+fullname)

# guarda el registro de las descargas en un archivo


def save_accounts_dict(accounts: dict, perfils_file=perfils_file):
    log(f'Saveing the dictionary to {perfils_file} file')

    if len(accounts) == 0:
        return

    with open(perfils_file, "w") as fp:
        json.dump(accounts, fp, indent=4)

# carga el dicionario de registro de descargas del archivo


def load_accounts_dict(perfils_file=perfils_file):
    log(f'Loading accounts from {perfils_file} file')
    if not perfils_file in os.listdir():
        print(
            f"Error al cargar el registro de descargas, no extiste el archivo {perfils_file}")
        return {}

    with open(perfils_file, "r") as fp:
        accounts_dict = json.load(fp)

    return dict(accounts_dict)

# go to account and scrape their images


def get_images_from(account, max_images=max_images):
    log(f'Getting {max_images} images from {account}')

    driver.get('https://twitter.com/' + account)

    # Open carrusel
    try:
        carrusel = driver.find_element(
            By.XPATH, '//div[@class="css-1dbjc4n r-1iusvr4 r-16y2uox r-a5pmau r-bnwqim"][1]')
        carrusel.click()
    except:
        print('Error. Carrusel not finded')
        return

    # clic on next
    try:
        for i in range(max_images):
            next = driver.find_element(
                By.XPATH, '//div[@aria-label="Next slide"]')
            sleep(0.4)
            next.click()
    except:
        print('Error clicking Next on carrusel')

    # get the images
    imgs = driver.find_elements(By.XPATH, '//li//img[@alt="Image"]')
    imgs = [i.get_attribute('src') for i in imgs]

    # returns a list of image urls
    return imgs

# Listar todos los nombres de perfiiles


def list_following(account):
    log('Listing following accounts')

    path = 'https://twitter.com/'+account+'/following'
    driver.get(path)
    sleep(5)
    following_list = []
    following_list = driver.find_elements(
        By.XPATH, '//div[@data-testid="cellInnerDiv"]//div[@class="css-1dbjc4n r-1awozwy r-18u37iz r-1wbh5a2"]')
    following_list = [i.text for i in following_list]

    print(following_list)
    print(len(following_list))

    return following_list


def login_twitter():
    log('Logging to twitter')

    # Login to twitter
    driver.get("https://www.twitter.com/login")

    # login
    # set user
    username = driver.find_element(By.XPATH, '//input[@name="text"]')
    username.send_keys(keys.USER)

    # Click on "Next"
    btn_next = driver.find_element(By.XPATH, '//div[@role="button"][2]')
    btn_next.click()

    # set password
    password = driver.find_element(By.NAME, 'password')
    password.send_keys(keys.PASS)

    # click on login
    submit = driver.find_element(
        By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]')
    submit.click()

    sleep(2)


def print_dict(dictionary):
    print(json.dumps(dictionary, sort_keys=True, indent=4))


def url_to_dict(dictionary, img_weburl, account):
    log(f'Url {img_weburl} to dictionary in {account}')

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


def image_exist(folder:str, nombre:str):
    archivo = f'{nombre}.png'
    return archivo in os.listdir(folder)

def attack(account: str):
    log(f'Attacking {account}...')

    # obtiene una lista de urls de las imagenes
    image_url_list = get_images_from(account)

    # cancela el ataque si no hay imagenes
    if image_url_list == None:
        log('- No se encontraron imagenes')
        return

    ## descarga cada imagen de la lista --------------------------
    
    idx = 0 # contador para el nombre de las imagenes
    perfils_dict = load_accounts_dict() # carga el diccionario
    
    for web_url in image_url_list:
        # comprueba si la url existe en el diccionario, si existe: no la descarga
        if account not in perfils_dict.keys() or web_url not in perfils_dict.get(account):
            # descargar la imagen ---------------------------------
            folder = images_path + account
            download_image(web_url, folder, idx)
            perfils_dict = url_to_dict(perfils_dict, web_url, account)
            idx += 1
        else:
            log('- La imagen ya existe en el diccionario')
    
    save_accounts_dict(perfils_dict) # guarda el diccionario

def attack_list(perfils_list: list):
    for account in perfils_list:
        attack(account)


def log(msg):
    if verbose:
        print(f'log: {msg}')

# RECORDATORIO - Para funciones como esta, que realizan una acción a cada uno
# de los elementos de esa lista. Crea una función que solo se lo haga a un elemento y
# crea otra que reciba la lista y la itere


if __name__ == '__main__':
    verbose = True
    max_images = 4
    login_twitter()
    # cuentas = list(load_accounts_dict().keys())
    cuentas = ['meowinxi', 'Brananaxx']
    # attack_list(cuentas)
