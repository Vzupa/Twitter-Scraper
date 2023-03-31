import csv
import string
import traceback
from getpass import getpass
from lib2to3.pgen2 import driver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from datetime import datetime
import Skrivni_podatki


spanje_cas = 10


def remove_invalid_characters(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in s if c in valid_chars)


def preberiCard(card):
    """Prebere podatke iz enega tvita in vrne tuple z njimi"""
    uporabnisko_ime = card.find_element(By.XPATH,
                                        (Skrivni_podatki.handle_ime_cas + "/div[1]/div[1]/a[1]/div[1]/div[1]/span[1]/span[1]")).text
    handle = card.find_element(By.XPATH,
                               (Skrivni_podatki.handle_ime_cas + "/div[2]/div[1]/div[1]/a[1]/div[1]/span[1]")).text
    try:
        date_str = card.find_element(By.TAG_NAME, "time").get_attribute("datetime")
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        cas = dt.strftime('%Y-%m-%d %H:%M:%S')
    except NoSuchElementException:
        return

    body_prvi = card.find_element(By.XPATH, Skrivni_podatki.do_druge_cetrine).text
    body_drugi = card.find_element(By.XPATH, f"{Skrivni_podatki.do_cetrtine}/div[3]").text
    body = body_prvi + " " + body_drugi

    if body == " ":
        return

    retweet = card.find_element(By.XPATH, './/div[@data-testid="retweet"]').text
    reply = card.find_element(By.XPATH, './/div[@data-testid="reply"]').text
    likes = card.find_element(By.XPATH, './/div[@data-testid="like"]').text

    zaNazaj = (uporabnisko_ime, handle, cas, body, retweet, reply, likes)
    return zaNazaj


if __name__ == '__main__':
    # Setupam Chrome binary in grem na login page
    driver = webdriver.Chrome()
    driver.get("https://twitter.com/i/flow/login")
    sleep(spanje_cas)

    # Poisce input za email in ga izpolni
    input_email = driver.find_element(By.XPATH, "//input[@autocomplete='username']")
    input_email.send_keys(Skrivni_podatki.mail)
    input_email.send_keys(Keys.RETURN)
    print("login")
    sleep(spanje_cas)

    if "Enter your phone number or username" in driver.page_source:
        # Ce zahteva username, ga izpolni
        input_username = driver.find_element(By.XPATH, "//input[@data-testid='ocfEnterTextTextInput' and @value='']")
        input_username.send_keys(Skrivni_podatki.username)
        input_username.send_keys(Keys.RETURN)
        print("Vmesni verification")
        sleep(spanje_cas)

    # Poisce input za geslo in ga izpolni
    input_password = driver.find_element(By.XPATH, "//input[@autocomplete='current-password']")
    input_password.send_keys(Skrivni_podatki.geslo)
    input_password.send_keys(Keys.RETURN)
    print("geslo")
    sleep(spanje_cas)

    # Gre direkt kam cemo
    driver.get(fr"https://twitter.com/{Skrivni_podatki.handle}")
    print("na strani")
    sleep(spanje_cas)

    tweet_data = []
    tweet_ids = set()
    last_postion = driver.execute_script("return window.pageYOffset;")
    scrolling = True
    index = 0

    try:
        while scrolling:
            cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

            for card in cards[-1:-31:-1]:
                try:
                    podatki = preberiCard(card)
                except Exception as e:
                    continue

                if not podatki:
                    continue

                tweet_id = ''.join(podatki)
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    tweet_data.append(podatki)
                    print(index, end =" ")
                    print(podatki)
                    index += 1

            scroll_attempt = 0
            while True:
                sleep(spanje_cas)
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight / 2);')
                current_position = driver.execute_script("return window.pageYOffset;")
                if last_postion == current_position:
                    scroll_attempt += 1

                    if scroll_attempt >= 3:
                        scrolling = False
                        break
                    else:
                        print(f"scroll attempt: {scroll_attempt}")
                        sleep(spanje_cas)
                else:
                    last_postion = current_position
                    break
    except Exception as e:
        traceback.print_exc()
    finally:
        tweet_data = sorted(tweet_data, key=lambda x: x[2], reverse=True)

        if len(tweet_data) > 30:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            file_name = f"{Skrivni_podatki.handle}_{timestamp}.csv"
            file_name = "csv_output/" + remove_invalid_characters(file_name)

            with open(file_name, 'w', newline='', encoding='utf-8') as f:
                header = ['Uporabnisko ime', 'Handle', 'Cas', 'Body', 'Retweet', 'Reply', 'Likes']
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(tweet_data)

    print("konec")
    try:
        sleep(1000)
    finally:
        driver.close()