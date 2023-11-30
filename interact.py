#our api for instagram
from api import APIClient #interact with instagram
from api import Media #media functions and properties
from api import DataType #user data types
from api import FollowingStatus #following statuses

#logger object that can append logs to file
from logs import Logger

import time #waits
import datetime #current time

import random #choose random numbers and choose randomly from set

import math #do complex math operations like sqrt

logger = Logger("logs.txt")

client = APIClient()

client.login("yourusername", "yourpassword")

def get_user_rank(usernmae):
    follower_followers_amount = client.user_followers_amount(usernmae)
    follower_following_amount = client.user_following_amount(usernmae)
    follower_medias_amount = client.user_medias_amount(usernmae)

    print(f"followers = {follower_followers_amount}, following = {follower_following_amount}, medias = {follower_medias_amount}")
    try:
        return math.isqrt(follower_following_amount*follower_medias_amount)/((follower_followers_amount+1) << 2)
    except:
        print(f"failed to get accurate user rank to user {usernmae}")
        logger.log_failed_action(f"give accurate user rank to user {usernmae}")
        return 0

def write_users(users, start_from, write_to): #writes users into csv with their username, engagements, and rank
    user_list: [str] = []
    with open(write_to, 'r') as csvfile:
        file_list = csvfile.read().splitlines()
        for row in file_list:
            user_list.append(row.split(',')[0])

    with open(write_to, 'a') as csvfile:

        wealthy_users = 0
        fields = "username,engagements,rank,following status,time" + '\n'
        if (len(user_list) == 0):
            csvfile.write(fields)
        elif (user_list[0] != "username"):
            # writing the fields
            csvfile.write(fields)

        i = start_from - 1
        while i < len(users):
            user = users[i]
            print()
            if user in user_list:
                i += 1
                print("user already in list")
                continue
        
            rank = get_user_rank(user)
            if client.is_account_private(user):
                rank = 0
            
            if rank > 0:
                wealthy_users += 1

            new_row = (f"{user},1,{rank},{client.get_following_status(user)},{datetime.datetime.now()}")  + '\n'
            csvfile.write(new_row)
            logger.log_action(f"exported user {user}")
            
            csvfile.flush()
            print(f"exported user {i + 1} - {user}")

            i += 1

        print()
        print(f"exported {i} users.")
        print((f"{wealthy_users} wealthy users."))        

def export_followers(username_of_scraped, count : int, start_from: int = 1, filename = "followers.csv"): #export all followers of a user with their username, engagements, and rank
    
    def get_followers(username, amount : int): #returns dict of users following a user given username and amount
        print(f"getting {amount} followers for account with username {username}")
        followers = client.user_followers(username, amount)
        logger.log_extracted(DataType(1), username)
        return followers

    print()
    followers = get_followers(username_of_scraped, count)
    print(f"done getting followers - {len(followers)}")
    write_users(followers, start_from, filename)
    print()
    print(f"exported {len(followers)} followers' data to {filename}")
    
def engage_with_user(user_username):
    user_following_status = client.get_following_status(user_username)
    if user_following_status != FollowingStatus.not_following:
        return #if user is allready following us or if were folloing them

    user_medias = client.user_medias(user_username, 1000)
    user_medias_amount = 0
    try:
        user_medias_amount = len(user_medias)
    except:
        print(f"failed to engage with user {user_username} - user has no medias")
        logger.log_failed_action(f"interact with user {user_username}")
        return

    user_medias_to_interact_amount = math.isqrt(user_medias_amount) #how many medias to interact with, square root of posts of user (like>comment)
    user_medias_to_interact : [Media] = random.sample(user_medias, user_medias_to_interact_amount) #choose that many medias to interact with
    
    user_medias_to_comment_amount = user_medias_to_interact_amount // 2 #how many medias to comment on
    user_medias_to_comment : [Media] = random.sample(user_medias_to_interact, user_medias_to_comment_amount)#chose medias to comment on from liked medias

    for user_media_to_interact in user_medias_to_interact: #like chosen medias
        client.media_like(user_media_to_interact) #like media

        print(f"liked media {user_media_to_interact}")
        
        if user_media_to_interact in user_medias_to_comment: #if current media is also supposed to be commented on
            def comment_on_media(media):
                with open("comments.txt", "r") as comments_file_list:
                    comments = comments_file_list.read().splitlines()
                    comment = comments[random.randint(0, len(comments) - 1)]
        
                    client.media_comment(media, comment)

                    return comment
                
            print(f"commented {comment_on_media(user_media_to_interact)} on media {user_media_to_interact}")
            
            
        print("pausing")
        time.sleep(random.randint(2, 5)) # to not get banned
        print("done pausing, next media")
    
    client.user_follow(user_username)

def engage_with_users(users_filepath, users_to_engage_with, last_users):
    with open(users_filepath, "r") as users_document:
        print("openeing file with users")
        users_data_list = users_document.read().splitlines()[-last_users:]
        user_rank_to_user_list = []
        
        i = 1
        while(i < len(users_data_list)): #create list with just rank and user id
            user_data_list = users_data_list[i].split(',')
            i += 1

            user = user_data_list[0]
            user_rank = float(user_data_list[2])
            user_rank_to_user_list.append((user_rank, user))

        user_rank_to_user_list.sort() #sort list by rank, lowest rank will come first
        num_of_users = len(user_rank_to_user_list)
        i = num_of_users - 1
        while(user_rank_to_user_list[i][0] > 0 and (num_of_users - i) <= users_to_engage_with):
            print()
            print(f"engaging with user {user_rank_to_user_list[i][1]} with rank {user_rank_to_user_list[i][0]}")
            engage_with_user(user_rank_to_user_list[i][1])
            i += -1
            def min(a, b) -> int:
                if a <= b:
                    return a
                else:
                    return b
            client.wait_random(4, 4) # to not get banned
        logger.log_action(f"engaged with {num_of_users - i} users")
        print(f"engaged with {num_of_users - i} users")

filename_to_export = "followers.csv"
username_to_scrape = "username of ig user in your nieche"
follower_to_scrape = 500
#export_followers(username_to_scrape, follower_to_scrape, 1, filename_to_export) #write followers and their data to csv file
print()
print("run engagement with top followers? enter amount of followers to engage with")
amount_of_followers_to_engage_with = int(input())
print(f"engaging with a maximum of {amount_of_followers_to_engage_with} users.")
engage_with_users(filename_to_export, 300, amount_of_followers_to_engage_with)
