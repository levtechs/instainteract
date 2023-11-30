from selenium import webdriver #allows us to open browser
from selenium.webdriver.common.by import By #allows us to use element selection
from selenium.webdriver.common.keys import Keys #allowes us to interact with elements via keyboard, using specific keys

import re #complex string manipulation

import random #random selection and random numbers

import time #wait

def wait():
    while input() != "q":
        time.sleep(0.1)

from enum import Enum

class MediaType(Enum):
    photo = 0
    carousel = 1
    reel = 2

class FollowingStatus(Enum):
    not_following = 0
    following = 1
    follow_back = 2
    requested = 3

class DataType(Enum):
    medias = 0
    followers = 1
    following = 2

class Media(object):
    #soemthing like "/p/XxxxXXxxxxX/"
    media_id : str = None
    media_url: str = None

    media_type: MediaType = None
    caraousel_photos_amount: int = None
    
    media_creator_username: str = None
    media_caption: str = None
    media_comments: [str] = None

    def extract_id_from_url(self, url):
        pattern = r'https://www.instagram.com/p/([a-zA-Z0-9_-]+)/'
        match = re.search(pattern, url)
    
        if match:
            return match.group(1)
        else:
            return None

    def __init__(self, media_id: str, media_url, media_type: MediaType = None, caraousel_photos_amount: int = None):
        self.media_id = media_id
        self.media_url = media_url
        self.media_type = media_type
        self.caraousel_photos_amount = caraousel_photos_amount

        if media_url == None and media_id != None:
            self.media_url = (f"https://www.instagram.com{media_id}")
        if media_url != None and media_id == None:
            self.media_id = self.extract_id_from_url(media_url)

    def get_media_type(self, media_id: str = None):
        if media_id == None:
            media_id = self.media_id
        pass

    def get_media_creator_username(self):
        pass

    def get_media_caption(self):
        pass

    def get_media_comments(self):
        pass

from logs import Logger
logger = Logger("logs.txt")

class APIClient(object):
    
    browser = webdriver.Chrome()

    def wait_random(self, min: float = 1, range: float = 1):
        time.sleep(random.uniform(min, min + range))

    def login(self, username: str, password: str):
        b = self.browser
        
        try:
            b.get("https://www.instagram.com/")
            self.wait_random(1, 2)
        except:
            print("failed to open instagram.com")
            logger.log_failed_action(f"open instagram.com")
        self.wait_random(1, 2)
        try:
            username_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[1]/div/label/input"
            try:
                b.find_element(By.XPATH, username_xpath).send_keys(str(username))
            except:
                print("couldnt find username text feild")
            time.sleep(0.5)

            password_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[2]/div/label/input"
            b.find_element(By.XPATH, password_xpath).send_keys(str(password))
            time.sleep(0.5)

            login_button_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button"
            b.find_element(By.XPATH, login_button_xpath).click()

            login_url = "https://www.instagram.com/accounts/onetap/?next=%2F"

            i = 0
            while b.current_url != login_url:
                time.sleep(0.1)
                i += 0.1
                if i > 20:
                    raise TimeoutError
            self.wait_random(0.5, 1)
            logger.log_action("logged in")
        except:
            print(f"couldn't log in using credentials: username: {username}, password: {password}")
            logger.log_failed_action("login")

    def get_user_page(self, username: str):
        return (f"https://www.instagram.com/{username}/")

    #scraping functions

    def cast_to_int(self, string: str):
        resultant_string = ""
        for alphabet in string:
            if alphabet != ",":
                resultant_string = resultant_string + alphabet

        return int(resultant_string)

    def user_medias_amount(self, username: str) -> int:
        b = self.browser
        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)
        else:
            self.wait_random(min = 0)
        medias_text_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[1]/span/span"
        return self.cast_to_int(b.find_element(By.XPATH, medias_text_xpath).text)

    def user_followers_amount(self, username: str) -> int:
        b = self.browser
        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)
        else:
            self.wait_random(min = 0)
        try:
            followers_text_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/a/span"
            try: #account isn't private
                try:
                    return self.cast_to_int(b.find_element(By.XPATH, followers_text_xpath).get_attribute('title'))
                except:
                    return self.cast_to_int(b.find_element(By.XPATH, followers_text_xpath).text)
            except: #account is private
                followers_text_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/span"
                try: #has more than one follower
                    return self.cast_to_int(b.find_element(By.XPATH, followers_text_xpath).get_attribute('title'))
                except: #has one follower
                    followers_text_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/span/span"
                    return self.cast_to_int(b.find_element(By.XPATH, followers_text_xpath).text)
        except:
            print(f"failed to find user followers amount of user {username}")
            logger.log_failed_action(f"find user followers amount of user {username}")

    def user_following_amount(self, username: str) -> int:
        b = self.browser
        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)
        else:
            self.wait_random(min = 0)
        following_text_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[3]/a/span/span"
        try: #account isn't private
            return self.cast_to_int(b.find_element(By.XPATH, following_text_xpath).text)
        except: #acount is private
            try:
                following_text_xpath = "//html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[3]/span/span"
                return self.cast_to_int(b.find_element(By.XPATH, following_text_xpath).text)
            except:
                print(f"failed to get user following amount for user {username}")
                logger.log_failed_action(f"get user following amount of user {username}")
                return None

    def get_following_status(self, username: str) -> FollowingStatus:
        b = self.browser
        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)

        not_following_xpath_public = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button/div/div"
        not_following_xpath_private = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div/button/div/div"

        following_xpath_public = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button/div/div[1]"
        
        follow_back_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button/div/div"

        requested_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div/button/div/div"

        output: FollowingStatus = 0
        try:
            try:
                try:
                    try:
                        try:
                            if b.find_element(By.XPATH, not_following_xpath_public).text == "Follow":
                                return FollowingStatus(0)
                            elif b.find_element(By.XPATH, following_xpath_public).text == "Following":
                                return FollowingStatus(1)
                            else:
                                print("couldn't find proper text indicating following status - Follow")
                                return None
                        except:
                            if b.find_element(By.XPATH, not_following_xpath_private).text == "Follow":
                                return FollowingStatus(0)
                            else:
                                print("couldn't find proper text indicating following status - Follow")
                                return None
                    except:
                        if b.find_element(By.XPATH, following_xpath_public).text == "Following":
                            return FollowingStatus(1)
                        else:
                            print("couldn't find proper text indicating following status - Following")
                            return None
                except:
                    if b.find_element(By.XPATH, follow_back_xpath).text == "Follow Back":
                        return FollowingStatus(2)
                    else:
                        print("couldn't find proper text indicating following status - Follow Back")
                        return None
            except:
                if b.find_element(By.XPATH, requested_xpath).text == "Requeted":
                    return FollowingStatus(3)
                else:
                    print("couldn't find proper text indicating following status - Requested")
                    return None
        except:
            print("unclear following status")
            logger.log_failed_action(f"find following status of {username}")
            return None
        
    def min(a, b):
        if a <= b:
            return a
        else:
            return b
        
    def is_account_private(self, username: str) -> bool:
        b = self.browser
        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)        
        test_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[1]/div/h2"
        #this element only appears on private accoutns
        test_element = None
        try:
            test_element = b.find_element(By.XPATH, test_xpath)
            #if succeeded, then private
        except:
            pass #couldn't find the element that 
        return test_element != None #if not none, then element was found meaning account was private

    def user_followers(self, username: str, count: int) -> [str]:

        if self.is_account_private(username):
            return None #can't get followers of private account even if it has them

        b = self.browser

        followers_to_get = min(count, self.user_followers_amount(username))

        url = (f"{self.get_user_page(username)}followers/")
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)
        
        followers_usernmaes = []

        current_follower_index = 1
        while current_follower_index <= followers_to_get:
            xpath = (f"/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[{current_follower_index}]/div/div/div/div[2]/div/div/div/div/div/a/div/div/span")

            element = None

            while element == None:
                try:
                    element = b.find_element(By.XPATH, xpath)
                except:
                    self.wait_random(0.2, 1)
                    list_xpath = "/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]"
                    element_to_scroll_within = b.find_element(By.XPATH, list_xpath)
                    scroll_script = "arguments[0].scrollBy(0, 500);"
                    b.execute_script(scroll_script, element_to_scroll_within)

            current_follower_username = element.text
            print(current_follower_username)
            followers_usernmaes.append(current_follower_username)
            current_follower_index += 1

        return followers_usernmaes

    def user_following(self, username: str, count: int) -> [str]:
        pass

    def user_medias(self, username: str, count: int) -> [Media]:

        if self.is_account_private(username):
            return None #can't get followers of private account even if it has them
           
        b = self.browser

        medias_to_get = min(min(count, self.user_medias_amount(username)), 20)

        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)

        medias = []

        remainder = medias_to_get % 3
        full_rows = int((medias_to_get - remainder)/3)
        current_row_index = 1
        
        def get_post_link_xpath(current_row_index, post_in_row, type):
            if type == 1:
                return (f"/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[2]/article/div/div/div[{current_row_index}]/div[{post_in_row}]/a")
                     #/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[3]/article/div[1]/div/div[{current_row_index}]/div[{post_in_row}]/a
            else:
                return (f"/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[3]/article/div[1]/div/div[{current_row_index}]/div[{post_in_row}]/a")
        while current_row_index <= full_rows:
            post_in_row = 1
            while post_in_row <= 3:
                
                post_href = None
                while post_href == None:
                    try:
                        try:
                            post_href = b.find_element(By.XPATH, get_post_link_xpath(current_row_index, post_in_row, 2)).get_attribute("href")
                        except:
                            post_href = b.find_element(By.XPATH, get_post_link_xpath(current_row_index, post_in_row, 1)).get_attribute("href")
                    except:
                        self.wait_random(0.2, 1)
                        b.execute_script("window.scrollTo(0, window.scrollY + 200)")

                medias.append(Media(media_id=None, media_url=post_href))
                post_in_row += 1

            current_row_index += 1

        if remainder > 0:
            post_in_row = 1
            while post_in_row <= remainder:
                post_href = None
                while post_href == None:
                    try:
                        try:
                            post_href = b.find_element(By.XPATH, get_post_link_xpath(current_row_index, post_in_row, 2)).get_attribute("href")
                        except:
                            post_href = b.find_element(By.XPATH, get_post_link_xpath(current_row_index, post_in_row, 1)).get_attribute("href")
                    except:
                        self.wait_random(0.2, 1)
                        b.execute_script("window.scrollTo(0, window.scrollY + 200)")
                
                medias.append(Media(media_id=None, media_url=post_href))
                post_in_row += 1
        
        return medias

    def extract_data(self, data_type: DataType, username: str):
        switch = {
            DataType.medias: self.user_medias(),
            DataType.followers: self.user_followers(),
            DataType.following: self.user_following(),
        }
        extract_function = switch.get(data_type, lambda: "Invalid Media Type")
        result = extract_function(data_type)
        return result

    def get_media_caption(self, media: Media):
        b = self.browser
        url = media.media_url
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)

        caption_xpath = "/html/body/div[8]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]/div[1]/h1"
        try:
            return b.find_element(By.XPATH, caption_xpath).text
        except:
            print("couldn't find caption")
            logger.log_failed_action(f"find caption on media {media.media_id}")
            return None

    #interaction functions

    def media_like(self, media: Media) -> bool: #(sucessful)
        b = self.browser

        url = media.media_url
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)

        like_button = None
        button_xpath1 = "/html/body/div[8]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[1]/span[1]/div/div/span"
        button_xpath2 = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div[1]/div/div[2]/div/div[3]/div[1]/div[1]/span[1]/div/div/span"
        try:
            like_button = b.find_element(By.XPATH, button_xpath1)
        except:
            try:
                like_button = b.find_element(By.XPATH, button_xpath2)
            except:
                print(f"couldn't like media {media.media_id}")
                logger.log_failed_action(f"like media {media.media_id}")
                return False
        like_button.click()
        logger.log_like(media)
        self.wait_random(2, 2)
        return True

    def media_comment(self, media: Media, comment: str) -> bool: #(sucessful)
        b = self.browser

        url = media.media_url
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)

        try:
            comment_box_xpath = "/html/body/div[8]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[3]/div/form/div/textarea"
            b.find_element(By.XPATH, comment_box_xpath).send_keys(f"{comment}{Keys.ENTER}")
            logger.log_comment(media, comment)
            time.sleep(7, 5)
            return True
        except:
            print(f"couldn't leave comment on media {media.media_id}")
            logger.log_failed_action(f"comment {comment} on media {media.media_id}")
            return False

    def user_follow(self, username: str) -> bool: #(sucessful)
        b = self.browser

        following_staus = self.get_following_status(username)
        if following_staus == FollowingStatus(1) or following_staus == FollowingStatus(3): #already following
            print("already following user")
            return False

        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)
        
        button_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button"
        try:
            b.find_element(By.XPATH, button_xpath).click()
            logger.log_follow(username)
            self.wait_random(2, 2)
            return True
        except:
            print("couldn't follow user")
            logger.log_failed_action(f"follow user {username}")
            return False
        
    def user_unfollow(self, username: str) -> bool: #(sucessful)
        b = self.browser

        following_staus = self.get_following_status(username)
        if following_staus == FollowingStatus(0) or following_staus == FollowingStatus(2): #not following
            print("not following user")
            return False
        
        url = self.get_user_page(username)
        if b.current_url != url:
            b.get(url)
            self.wait_random(4, 2)
        
        button_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button"
        try:
            b.find_element(By.XPATH, button_xpath).click()
            logger.log_unfollow(username)
            self.wait_random(2, 2)
            return True
        except:
            print("couldn't unfollow user")
            logger.log_failed_action(f"unfollow user {username}")
            return False