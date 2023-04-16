from pymongo import MongoClient
import pymongo
import os
from dotenv import load_dotenv
import certifi
from flask import Flask
from flask_bcrypt import Bcrypt
import bcrypt
import random
import string
import logging
import boto3
from botocore.exceptions import ClientError
import os
import datetime

load_dotenv()

app = Flask('')

bcrypt = Bcrypt(app)

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
CLUSTER_NAME = os.getenv('CLUSTER_NAME')

client = pymongo.MongoClient(f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_NAME}.feo8fhy.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())

db = client.test

# Collection Name
col = db["users"]

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')

#session = boto3.Session( aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def upload_file(file_name, bucket, object_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)


    # Upload the file
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


#clear folder in s3 bucket with username and which folder to clear
def clear_folder(folder):
    username = username.replace(" ", "")
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('mybucket')
    bucket.objects.filter(Prefix=folder).delete()
    print(f"folder cleared {folder}")

#delete file from s3 bucket with username and file name
def delete_file(file_name, bucket):
    username = username.replace(" ", "")
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.objects.filter(file_name).delete()
    


#get all usernames that contain the search query
def search_users(search_query):
    search_query2 = str(search_query)
    col2 = db["users"]
    myquery = {"username": {"$regex": search_query2}}
    mydoc = col2.find(myquery)
    list_users = []
    list_profile_urls = []
    list_bios = []
    for x in mydoc:
        list_users.append(x["username"])
        list_profile_urls.append(x["profile_image"])
        bio = x["bio"]
        if bio == "click to add bio":
            bio = "This user has not added a bio yet"
        list_bios.append(bio)
    return list_users, list_profile_urls, list_bios



#insert email, key and password
def insert(username, email, password, code, verified):  
    username = username.replace(" ", "")

    if "/" in username:
        username = username.replace("/", "_")
    #encrypt password with bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    #generate 15 character string
    user_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 20))

    #if user_id is already in the database, generate a new one
    while user_id in pull_keys():
        user_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 20))
        print("new user_id generated")

    
    #print all emails from the collection "users"
    mydoc = col.find()
    for x in mydoc:
        if x["email"] == email:
            print("email already exists")
            return False
        else:
            pass
            print("email does not exist")


    profile_url = "profile/" + username

    mydict = {
        "email": email, 
        "username": username, 
        "password": hashed_password, 
        "verified": verified, 
        "profile_url": profile_url,
        "user_id": user_id,
        "code": code}

    col.insert_one(mydict)


    username = username.replace(" ", "")
    myquery = {"username": username}
    newvalues = {"$set": {"bio": "click to add bio"}}
    col.update_one(myquery, newvalues)

    newvalues = {"$set": {"fun_fact": "click to add a fun fact"}}
    col.update_one(myquery, newvalues)

    newvalues = {"$set": {"profile_image": "files/profile_basic.png"}}
    col.update_one(myquery, newvalues)

    

#add username to "users_posts" collection
def add_user_posts(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    mydict = {"username": username}
    col3.insert_one(mydict)


#check if element exists in the database
def check(username, email, password):
    username = username.replace(" ", "")
    print("checking")
    myquery = {"email": email, "username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        if bcrypt.check_password_hash(x["password"], password):
            return True
        else:
            return False


col2 = db["users"]


#pull all keys from database
def pull_keys():
    
    list_keys = []

    mydoc = col2.find()
    for x in mydoc:
        list_keys.append(x)
    
    return list_keys


#is user verified?
def is_verified(email):
    myquery = {"email": email}
    mydoc = col.find(myquery)
    for x in mydoc:
        if x["verified"] == True:
            return True
        else:
            return False

def email_exists(email):
    myquery = {"email": email}
    mydoc = col.find(myquery)
    for x in mydoc:
        return True


#check if username exists in database and return true if it does
def username_exists(username):
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        return True


#return object with username and email from database
def get_user(username):
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        return x

#edit verified in database 
def edit_verified(username, code):
    username = username.replace(" ", "")
    myquery = {"username": username}
    newvalues = {"$set": {"verified": True}}
    #print the code that is in the same object as the username
    col.update
    mydoc = col.find(myquery)
    for x in mydoc:
        print(x["code"])
        if int(x["code"]) == int(code):
            col.update_one(myquery, newvalues)
            return True
        else:
            return False

#check if user is verified
def is_verified(username):
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        if x["verified"] == True:
            return True
        else:
            return False


#add new element to database with username
def add_element(username, bio):
    username = username.replace(" ", "")
    myquery = {"username": username}
    
    #update bio in database
    newvalues = {"$set": {"bio": bio}}
        
    col.update_one(myquery, newvalues)


#pull bio from database with username and return it 
def pull_bio(username):
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        return x["bio"]


#pull fun fact from database with username and return it
def pull_fun_fact(username):
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        return x["fun_fact"]

#update fun_fact in database
def update_fun_fact(username, fun_fact):
    username = username.replace(" ", "")
    myquery = {"username": username}
    newvalues = {"$set": {"fun_fact": fun_fact}}
    col.update_one(myquery, newvalues)


#create an object called "posts" and then isnert a new nested row under "posts" with the username
def add_posts(username, post_location, url, description, story):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    #get current time in UTC and format it to a string and abbreviated format
    time = datetime.datetime.utcnow().strftime("%b %d %H:%M")
    newvalues = {"$push": {"post_location": post_location, "post_time": time, "post_url": url, "description": description, "story": story}}
    col3.update_one(myquery, newvalues)

#pull all posts from database
def pull_posts(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    try:
        for x in mydoc:
            return x["post_location"]
    except:
        pass

#pull all post times from database
def pull_post_times(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    try:
        for x in mydoc:
            return x["post_time"]
    except:
        pass


#pull all post urls from database
def pull_post_urls(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    try:
        for x in mydoc:
            return x["post_url"]
    except:
        pass

#delete all contents of folder in S3
def delete_folder(bucket_name, folder_name):
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)
    bucket.objects.filter(Prefix=folder_name).delete()

#add profile_image file_location to database
def add_profile_image(username, file_location):
    username = username.replace(" ", "")
    myquery = {"username": username}
    newvalues = {"$set": {"profile_image": file_location}}
    col.update_one(myquery, newvalues)


#pull profile_image file_location from database
def pull_profile_image(username):
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        return x["profile_image"]


#create an object called "friends" and then insert a new nested row under "friends" with the username
def add_friends(username, friend_username):
    col4 = db["users_friends"]
    username = username.replace(" ", "")
    friend_username = friend_username.replace(" ", "")
    myquery = {"username": username}
    newvalues = {"$push": {"friend_username": friend_username}}
    col4.update_one(myquery, newvalues)


#pull all post descriptions from database
def pull_post_descriptions(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    try:
        for x in mydoc:
            return x["description"]
    except:
        pass


#pull all post stories from database
def pull_post_stories(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    try:
        for x in mydoc:
            return x["story"]
    except:
        pass

#get the row number where post location is equals to a variable
def get_row_number(username, post_location):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        return x["post_location"].index(post_location)

#pull post_time, post_url, description, and story from database using username and index number
def pull_post_info(username, index):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        post_time = x["post_time"][index]
        post_url = x["post_url"][index]
        description = x["description"][index]
        story = x["story"][index]
        return post_time, post_url, description, story


#get all files in folder in S3
def get_files(bucket_name, folder_name):
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)
    return [obj.key for obj in bucket.objects.filter(Prefix=folder_name)]



#get profile url with username
def get_profile_url(username):
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col.find(myquery)
    for x in mydoc:
        return x["profile_url"]


#get all profile urls that contain a certain username
def get_profile_urls(username):
    myquery = {"username": {"$regex": username}}
    mydoc = col.find(myquery)
    for x in mydoc:
        return x["profile_url"]

#get all queries that contain a certain username
def get_queries(username):
    myquery = {"username": {"$regex": username}}
    mydoc = col.find(myquery)
    for x in mydoc:
        return x["username"]



#get 10 of the most recent posts posted and return the post url
def get_recent_posts():
    col3 = db["users_posts"]
    mydoc = col3.find().sort("post_time", -1).limit(10)
    list_post_urls = []
    for x in mydoc:
        list_post_urls.append(x["post_url"])

    return list_post_urls



#get all usernames from database
def get_usernames():
    mydoc = col.find()
    all_usernames = []
    for x in mydoc:
        all_usernames.append(x["username"])
    return all_usernames

#get recent_post value from database using username
def get_recent_post(username):
    myquery = {"username": username}
    mydoc = col.find(myquery)

    for x in mydoc:
        return x["recent_post"]


#get 3 random usernames, with a while loop check if they have any posts, and if they do, get a random post from them and when the list has 3 elements in it return a list of the post urls and usernames, if they dont have any posts, get a new random username
def get_random_post():

    list_post_urls = []
    list_usernames = []

    while len(list_post_urls) < 3:
        random_username = random.choice(get_usernames())
        print(random_username)
        try:
            if get_recent_post(random_username) != None or "none" or "":
                print(get_recent_post(random_username))
                #get a random post from the random username
                random_post = random.choice(pull_post_urls(random_username))
                print(random_post)
                list_post_urls.append(random_post)
                list_usernames.append(random_username)
            else:
                print(get_recent_post(random_username))
                pass
        except:
            pass
    return list_post_urls, list_usernames




#in user_posts, add a new row called "recently_posted" and set it to the current time in UTC format seconds:minutes:hours:day:month:year
def add_recently_posted(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}

    now = datetime.datetime.utcnow()
    now = now.strftime("%S:%M:%H %d:%m:%Y")

    newvalues = {"$set": {"recent_post": now}}
    col3.update_one(myquery, newvalues)






#get 4 usernames with the 4 most recent "recent_post" values in very importnat UTC format (seconds:minutes:hours day:month:year)
def get_recently_posted():
    col3 = db["users_posts"]
    mydoc = col3.find().sort("recent_post", -1).limit(4)
    list_of_usernames = []
    list_of_recent_posts = []
    try:
        for x in mydoc:
            list_of_usernames.append(x["username"])
            myquery = {"username": x["username"]}
            mydoc = col3.find(myquery)
            for x in mydoc:
                list_of_recent_posts.append(x["post_url"][-1])
    except:
        pass

    return list_of_usernames, list_of_recent_posts






#pull all "recent_post" values from database and sort them in ascending order, if recent_post is none, skip it
def get_recent_posts():
    col3 = db["users_posts"]
    mydoc = col3.find().sort("recent_post", -1).limit(4)
    list_of_usernames = []
    list_of_recent_posts = []
    for x in mydoc:
        list_of_usernames.append(x["username"])
        myquery = {"username": x["username"]}
        mydoc = col3.find(myquery)
        for x in mydoc:
            list_of_recent_posts.append(x["post_url"][-1])
    return list_of_usernames, list_of_recent_posts





#get most recent post from username
def get_recent_post(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        return x["post_url"][0]


#like a post
def like_post(username, post_url, which):
    col3 = db["users_posts"]
    myquery = {"post_url": post_url}

    try:
        if which == "like_button":
            newvalues = {"$set": {"post_like_dislikes": {post_url: {"$push": {"likes": username}}}}}
            col3.update_one(myquery, newvalues)
            print(f"{username} pressed like button on {post_url}")
        elif which == "dislike_button":
            newvalues = {"$set": {"post_like_dislikes": {post_url: {"$push": {"dislikes": username}}}}}
            col3.update_one(myquery, newvalues)
            print(f"{username} pressed dislike button on {post_url}")
        else:
            print("nothing happened")
            pass
    except:
        print("error")
        pass


#look if post_url exists using username and return the index of the post_url
def get_post_index(username, post_url):
    print("ran first for loop")
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        return x["post_url"].index(post_url)




#delete post_url, description, post_location, post_time and story using get_post_index using index and username
def remove_post_good(username, post_url):
    print("ran second for loop")
    col3 = db["users_posts"]
    print("ran second for loop2")
    myquery = {"username": username}
    print("ran second for loop3")
    index = get_post_index(username, post_url)
    print(f"index is {index}")
    print("ran second for loop4")
    newvalues = {"$unset": {"post_url": [index], "description": [index], "post_location": [index], "post_time": [index], "story": [index]}}
    print("ran second for loop5")
    col3.update_one(myquery, newvalues)
    print("ran second for loop6")
    print(f"{username} deleted {post_url}")


#remove post_url by its index "5"
def remove_post_url(username, post_url):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    index = get_post_index(username, post_url)
    for x in mydoc:
        post_url = x["post_url"]
        description = x["description"]
        post_location = x["post_location"]
        post_time = x["post_time"]
        story = x["story"]

        post_url.remove(post_url[index])
        description.remove(description[index])
        post_location.remove(post_location[index])
        post_time.remove(post_time[index])
        story.remove(story[index])

        newvalues = {"$set": {"post_url": post_url, "description": description, "post_location": post_location, "post_time": post_time, "story": story}}
        col3.update_one(myquery, newvalues)


#check if friends object is empty, and if it does return false, secondly check if friend exists in database using username and friend_username and return true if friend exists
def check_friend(username, friend_username):
    col3 = db["users"]
    username = username.replace(" ", "")
    friend_username = friend_username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    list_friends = []
    for x in mydoc:
        try:
            if x["friends"] == []:
                return False

            for i in x["friends"]:
                    list_friends.append(i["all"][1])

            if friend_username in list_friends:
                return True
            else:
                return False


        except:
            return False




        


#add both usernames in one line under "friends" array in database
#and create friends array if it doesn't exist
def add_friends(username, friend_username):
    col3 = db["users"]
    username = username.replace(" ", "")
    friend_username = friend_username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        try:
            if check_friend(username, friend_username) == False:
                newvalues = {"$push": {"friends": {"all": [username, friend_username, "no"]}}}
                col3.update_one(myquery, newvalues)
            else:
                remove_friend(username, friend_username)

        except:
            pass



#get all friends from database
def get_friends(username):
    col3 = db["users"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    list_of_friends = []
    for x in mydoc:
        try:
            for i in x["friends"]:
                
                list_of_friends.append(i["all"][1])
        except:
            pass
    return list_of_friends


#remove friend and array from database using username and friend_username
def remove_friend(username, friend_username):
    col3 = db["users"]
    username = username.replace(" ", "")
    friend_username = friend_username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        try:
            newvalues = {"$pull": {"friends": {"all": [username, friend_username, "no"]}}}
            col3.update_one(myquery, newvalues)
            print(f"{username} removed {friend_username} as a friend")
        except:
            pass


#get last post from username
def get_last_post(username):
    col3 = db["users_posts"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        try:
            post_url = x["post_url"][-1]
            description = x["description"][-1]
            post_location = x["post_location"][-1]
            post_time = x["post_time"][-1]
            story = x["story"][-1]
            return post_url, description, post_location, post_time, story
        except:
            pass










#get all followers from username in database
def get_followers(username):
    col3 = db["users"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    list_of_followers = []
    for x in mydoc:
        try:
            for i in x["followers"]:
                list_of_followers.append(i)
        except:
            pass
    print(f"all followers of {username} are {list_of_followers}")
    return list_of_followers

#get all following from username in database
def get_following(username):
    col3 = db["users"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    list_of_following = []
    for x in mydoc:
        try:
            for i in x["following"]:
                list_of_following.append(i)
        except:
            pass
    
    print(f"all following of {username} are {list_of_following}")
    return list_of_following

#check if username is following follower_username
def check_following(username, follower_username):
    col3 = db["users"]
    username = username.replace(" ", "")
    follower_username = follower_username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    list_following = []
    for x in mydoc:
        try:
            if x["following"] == []:
                return False

            for i in x["following"]:
                    list_following.append(i)

            if follower_username in list_following:
                return True
            else:
                return False


        except:
            return False


#remove follower from database using username and follower_username
def remove_follower(username, follower_username):
    col3 = db["users"]
    username = username.replace(" ", "")
    follower_username = follower_username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        try:
            newvalues = {"$pull": {"followers": follower_username}}
            col3.update_one(myquery, newvalues)
            print(f"{username} removed {follower_username} as a follower")
        except:
            pass

#remove following from database using username and follower_username
def remove_following(username, follower_username):
    col3 = db["users"]
    username = username.replace(" ", "")
    follower_username = follower_username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        try:
            newvalues = {"$pull": {"following": follower_username}}
            col3.update_one(myquery, newvalues)
            print(f"{username} removed {follower_username} as a following")
        except:
            pass





#add new follower under array "followers" in database and create array if it doesn't exist, and check if follower already exists
def add_follower(username, follower_username):
    col3 = db["users"]
    username = username.replace(" ", "")
    follower_username = follower_username.replace(" ", "")

    myquery = {"username": username}
    mydoc = col3.find(myquery)

    myquery2 = {"username": follower_username}
    mydoc2 = col3.find(myquery2)

    print(f"follower_username is {follower_username}")

    for x in mydoc:
        try:
            following_list = get_following(username)
            print(f"following list is {following_list}")
            if follower_username in following_list:
                remove_following(username, follower_username)
                print("removed following")
                pass
            else:
                newvalues = {"$push": {"following": follower_username}}
                col3.update_one(myquery, newvalues)

        except:
            pass
    
    for x in mydoc2:
        try:
            if username in get_followers(follower_username):
                remove_follower(follower_username, username)
                pass
            else:
                newvalues2 = {"$push": {"followers": username}}
                col3.update_one(myquery2, newvalues2)

        except:
            pass



#get all followers from username in database
def get_followers(username):
    col3 = db["users"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    list_of_followers = []
    for x in mydoc:
        try:
            for i in x["followers"]:
                list_of_followers.append(i)
        except:
            pass
    print(f"all followers of {username} are {list_of_followers}")
    return list_of_followers


#get profile image of username
def get_profile_image(username):
    col3 = db["users"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    for x in mydoc:
        try:
            profile_image = x["profile_image"]
            return profile_image
        except:
            pass


#get all following from username in database
def get_followingers(username):
    col3 = db["users"]
    username = username.replace(" ", "")
    myquery = {"username": username}
    mydoc = col3.find(myquery)
    list_of_following = []
    list_profile_image = []
    for x in mydoc:
        try:
            for i in x["following"]:
                list_of_following.append(i)
                list_profile_image.append(get_profile_image(i))
        except:
            pass
    
    print(f"all following of {username} are {list_of_following}")
    return list_of_following, list_profile_image