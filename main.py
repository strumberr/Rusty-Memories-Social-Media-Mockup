from cgi import print_arguments
from flask import Flask
from flask import render_template
from flask_login import LoginManager
from flask import Flask, render_template, request, redirect, flash, session
from flask import Flask, flash, redirect, render_template, request, url_for
from db import *
    
from db import search_users

import os
from email_snippet import emailsend
import random
from werkzeug.utils import secure_filename
import string

UPLOAD_FOLDER = 'users'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


app = Flask(__name__)

FLASK_KEY = os.getenv('FLASK_KEY')

app.secret_key = FLASK_KEY

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




@app.route('/', methods=["GET", "POST"])
def index():
    rmlogo = '/static/images_home/rmlogo3.png'
    trophy_most_liked = '/static/images_home/trophy_most_liked.png'
    rmlogo2 = '/static/images_home/rmlogo2.png'

    rm_logo_light = 'static/important_images/RM_logo.png'


    main_featured = get_random_post()
    random_post = main_featured[0]
    random_post_username = main_featured[1]


    recent_posts = get_recently_posted()
    recent_post_username = recent_posts[0]
    recent_post = recent_posts[1]


    if 'username' in session:
        signed_in = True
    else:
        signed_in = False

    if request.method == 'POST':

        search_field = request.form['search_field']

        print(search_field)
        
        all_users = search_users(search_field)

        users = all_users[0]

        profile_urls = all_users[1]

        list_bios = all_users[2]

        print(f"users: {users}")

        print("searched")



    try:
        if users == None or users == [] or not users:
            users = []
    except:
        users = []

    return render_template('index.html', 
    signed_in=signed_in,
    users=users,
    rm_logo_light=rm_logo_light, 
    recent_post_username=recent_post_username, 
    recent_post=recent_post,
    rmlogo=rmlogo, 
    random_post=random_post, 
    random_post_username=random_post_username, 
    trophy_most_liked=trophy_most_liked, 
    reversed=reversed, 
    zip=zip)




@app.route('/api/users/search/<query>', methods=["GET", "POST"])
def users_api(query):

    if query != "" or None:
        if len(query) >= 2:


            all_users = search_users(query)

            users = all_users[0]

            profile_urls = all_users[1]

            list_bios = all_users[2]

            json = {
                "users": users,
                "profile_urls": profile_urls,
                "list_bios": list_bios
            }

            return json
        else:
            return "hello"

        return "Hello, World!"
    
    return "hello"


@app.route('/profile', methods=["GET", "POST"])
def profile():

    if 'username' in session:
        user = session['username']

        settings_icon = 'static/images_home/settings_icon.png'

        home_icon = 'static/important_images/home_icon.png'

        search_icon = 'static/important_images/search_icon.png'

        create_icon = 'static/important_images/create_icon_new.png'

        if is_verified(user) == True:

            if request.method == 'POST':

                try:
                    bio = request.form['bio']
                    if len(bio) > 150:
                        description = description[:150]
                    if bio == "":
                        bio = "Tap here to add a bio!"
                    add_element(user, bio)


                    return redirect(url_for('profile'))

                except:
                    pass


                try:
                    fun_fact = request.form['fun_fact']
                    if len(fun_fact) > 100:
                        fun_fact = fun_fact[:100]
                    if fun_fact == "":
                        fun_fact = "Tap here to add a fun fact!"
                    update_fun_fact(user, fun_fact)

                    print(fun_fact)

                    return redirect(url_for('profile'))

                except:
                    pass






                try:
                    if 'file' not in request.files:

                        return redirect(post)

                    file = request.files['file']
                    # if user does not select file, browser also
                    # submit an empty part without filename
                    if file.filename == '':

                        return redirect(post)

                    
                    if file and allowed_file(file.filename):
                        print("file is allowed profile")

                        username = user

                        file_name_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 30))

                        # this will return a tuple of root and extension
                        split_tup = os.path.splitext(file.filename)
                        
                        # extract the file name and extension
                        file_extension = split_tup[1]


                        file.filename = f"users/{username}_profile_image_{file_name_string}{file_extension}"

                        filename = secure_filename(file.filename)

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        print("file saved successfully")

                        print(f" 222222users/{username}/profile_image/{file_name_string}{file_extension} profile")

                        print(f" 11111 users/{username}/profile_image/profile_image/{file_name_string}{file_extension} profile")

                        delete_folder("rustymemories", f"users/{username}/profile_image")

                        print("folder deleted successfully profile")

                        upload_file(f"users/users_{username}_profile_image_{file_name_string}{file_extension}", "rustymemories", f"users/{username}/profile_image/{file_name_string}{file_extension}")

                        print("file uploaded successfully 1 profile")

                        add_profile_image(username, f"users/{username}/profile_image/{file_name_string}{file_extension}")

                        print("file uploaded successfully 2 profile")

                        os.remove(f"users/users_{username}_profile_image_{file_name_string}{file_extension}")

                        return redirect(url_for('profile'))
                except:
                    pass


            bio = pull_bio(user)
            print(f"bio is {bio}")
            if str(bio) == None or "":
                bio = "Tap here to add a bio!"

            fun_fact = pull_fun_fact(user)
            if str(fun_fact) == None or "":
                fun_fact = "Tap here to add a fun fact!"

            all_posts = pull_posts(user)
            if all_posts == None:
                all_posts = ["no posts yet"]

            all_post_times = pull_post_times(user)
            if all_post_times == None:
                all_post_times = ["no posts yet"]

            all_post_urls = pull_post_urls(user)
            if all_post_urls == None:
                all_post_urls = ["no posts yet"]

            

            print(all_posts)

            try:
                profile_image = get_files("rustymemories", f"users/{user}/profile_image")
                profile_image = profile_image[0]
            except:
                if not profile_image:
                    profile_image = "files/profile_basic.png"

            print(profile_image)

            following_all = get_followingers(user)

            following = following_all[0]

            following_profile_url = following_all[1]


            return render_template('profile.html', 
            user=user, 
            all_posts=all_posts, 
            bio=bio, 
            following=following[0:4],
            following_num=len(following),
            following_profile_url=following_profile_url[0:4],
            settings_icon=settings_icon, 
            fun_fact=fun_fact, 
            profile_image=profile_image, 
            all_post_times=all_post_times, 
            all_post_urls=all_post_urls, 
            home_icon=home_icon,
            search_icon=search_icon,
            create_icon=create_icon,
            zip=zip, 
            reversed=reversed)
        else:
            return render_template("email_verify.html")




    
    return render_template("login.html")



@app.route('/profile/settings', methods=["GET", "POST"])
def profile_settings():

    return render_template('profile_settings.html')



@app.route('/signup', methods=["GET", "POST"])
def signup():

    if 'username' in session:
        return redirect(url_for('profile'))


    if request.method == "POST":

        email = request.form.get('email')
        if len(email) > 50:
            email = email[:50]
        email = str(email)

        password = request.form.get('password')
        if len(password) > 50:
            password = password[:50]
        password = str(password)

        username = request.form.get('username')
        if len(username) > 20:
            username = username[:20]
        username = str(username)


        if "@" in email:
            if email_exists(email) == True:
                flash("Email already exists, please log in!")
                return redirect(url_for('signup'))

            elif username_exists(username) == True:
                flash("Username already exists, look for a different one!")
                return redirect(url_for('signup'))

            else:
                code = random.randint(100000, 999999)
                emailsend(username, email, code)
                insert(username, email, password, code, verified=False)
                add_user_posts(username)
                print("email function main called")
                session['username'] = username
                user = session['username']
                return render_template("email_verify.html", user = user)
        else:
            flash("Please enter a valid email address!")
            return redirect(url_for('signup'))



    return render_template('signup.html')




@app.route('/login', methods=["GET", "POST"])
def login():

    if 'username' in session:
        return redirect(url_for('profile'))

    else:

        if request.method == "POST":

            email = request.form.get('email')
            if len(email) > 50:
                email = email[:50]
            email = str(email)

            password = request.form.get('password')
            if len(password) > 50:
                password = password[:50]
            password = str(password)

            username = request.form.get('username')
            if len(username) > 20:
                username = username[:20]
            username = str(username)

            if check(username, email, password) == True:
                #save user in session
                print("user exists")
                session['username'] = username
                user = session['username']
                return redirect(url_for('profile'))
            else:
                flash('Incorrect email or password')

        
    return render_template('login.html')



#create new app route that logs users out
@app.route('/logout', methods=["GET", "POST"])
def logout():
    #remove user from session
    session.pop('username', None)
    return redirect(url_for('signup'))


@app.route('/email_verify', methods=["GET", "POST"])
def email_verify():
    if 'username' in session:
        user = session['username']

        settings_icon = 'static/images_home/settings_icon.png'

        home_icon = 'static/important_images/home_icon.png'

        search_icon = 'static/important_images/search_icon.png'

        create_icon = 'static/important_images/create_icon_new.png'

        if request.method == "POST":
                
            code1 = request.form.get('verification_code1')
            code2 = request.form.get('verification_code2')
            code3 = request.form.get('verification_code3')
            code4 = request.form.get('verification_code4')
            code5 = request.form.get('verification_code5')
            code6 = request.form.get('verification_code6')

            code = code1 + code2 + code3 + code4 + code5 + code6

            print(code)

            if edit_verified(user, code) == True:

                try:
                    bio = request.form['bio']
                    add_element(user, bio)

                except:
                    pass


                try:
                    fun_fact = request.form['fun_fact']
                    update_fun_fact(user, fun_fact)
                    print(fun_fact)
                except:
                    pass


                bio = pull_bio(user)

                fun_fact = pull_fun_fact(user)

                all_posts = pull_posts(user)
                if all_posts == None:
                    all_posts = ["no posts yet"]

                profile_image = pull_profile_image(user)

                print(all_posts)

                return redirect(url_for('profile'))
            else:
                if (code == None or "" or "None"):
                    flash("Please enter a valid verification code")
                    return render_template("email_verify.html")
                else:
                    flash("Code is incorrect!")
                    return render_template("email_verify.html")



        return redirect(url_for('profile'))

    return render_template("email_verify.html", reversed=reversed, zip=zip)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/post', methods=["GET", "POST"])
def post():

    app.config['MAX_CONTENT_LENGTH'] = 16 * 2000 * 2000

    if 'username' in session:
    
        username = session['username']

        file_name_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 20))
    
        if request.method == 'POST':

            description = request.form.get('description')

            if len(description) > 512:
                description = description[:512]

            story = request.form.get('story')

            if len(story) > 512:
                story = story[:512]

            # check if the post request has the file part
            if 'file' not in request.files:

                return redirect("post")

            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':

                return redirect("post")


            if file and allowed_file(file.filename):

                file.filename = f"{username}/posts/{file_name_string}.png"

                filename = secure_filename(file.filename)

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                upload_file(f"users/{username}_posts_{file_name_string}.png", "rustymemories", f"users/{username}/posts/{file_name_string}")

                add_posts(username, f"users/{username}/posts/{file_name_string}", f"users/{username}/posts/{file_name_string}", str(description), str(story))

                os.remove(f"users/{username}_posts_{file_name_string}.png")

                add_recently_posted(username)

                return redirect("profile")


        return render_template("post.html", username=username)

    else:
        return render_template("login.html")









@app.route('/user4_posts/users/<username2>/posts/<id>', methods=["GET", "POST"])
def posts(username2=None, id=None):


    together = f"users/{username2}/posts/{id}"

    row_number = get_row_number(username2, together)

    all_data = pull_post_info(username2, int(row_number))
    
    url = f"users/{username2}/posts/{id}"

    if 'username' in session:
        username = session['username']

        if request.method == "POST":
                
            #get value of button clicked

            like_button = request.form.get('like_button')

            dislike_button = request.form.get('dislike_button')

            if like_button == "like_button":
                like_post(username, url, "like_button")
                print("like")
            elif dislike_button == "dislike_button":
                like_post(username, url, "dislike_button")
                print("dislike")


        return render_template("post_template.html", url=url, post=together, username=username2, all_data=all_data)

    return render_template("post_template.html", url=url, post=together, username=username2, all_data=all_data)



@app.route('/users/search', methods=["GET", "POST"])
def search_userios():

    if 'username' in session:
        username = session['username']


        if request.method == "POST":
                
            search_query = request.form.get('search')

            print(search_query)
            
            all_users = search_users(search_query)

            users = all_users[0]

            profile_urls = all_users[1]

            list_bios = all_users[2]

            print(all_users)

            return render_template("user_search.html", username=username, users=users, profile_urls=profile_urls, list_bios=list_bios, reversed=reversed, zip=zip)
    

        return render_template("user_search.html", username=username, reversed=reversed, zip=zip)


    return render_template("login.html")    


@app.route('/users/<variable>', methods=["GET", "POST"])
def public_profile(variable):


    if 'username' in session:

        username = session['username']

        if request.method == "POST":

            follow = request.form.get('follow')

            if follow == "follow":
                add_follower(username, variable)

                return redirect(url_for('public_profile', variable=variable))

        print(username)

        print(variable)

        if str(username) == str(variable):
            return redirect(url_for('profile'))
        else:
            pass

        settings_icon = 'static/images_home/settings_icon.png'

        home_icon = 'static/important_images/home_icon.png'

        search_icon = 'static/important_images/search_icon.png'

        create_icon = 'static/important_images/create_icon_new.png'

        if check_following(username, str(variable)) == True:
            friend = True
            print("friend true")
        else:
            friend = False
            print("friend false")

        username = variable

        bio = pull_bio(username)
        if str(bio) == "click to add bio" or None or "":
            bio = "This user hasn't added a bio yet!"

        fun_fact = pull_fun_fact(username)
        if str(fun_fact) == "click to add a fun fact" or None or "":
            fun_fact = "This user hasn't added a fun fact yet!"

        all_posts = pull_posts(username)
        if all_posts == None:
            all_posts = ["no posts yet"]

        all_post_times = pull_post_times(username)
        if all_post_times == None:
            all_post_times = ["no posts yet"]

        all_post_urls = pull_post_urls(username)
        if all_post_urls == None:
            all_post_urls = ["no posts yet"]



        

        print(all_posts)

        profile_image = pull_profile_image(username)

        print(profile_image)

        following_all = get_followingers(username)

        following = following_all[0]

        following_profile_url = following_all[1]

        return render_template('public_profile.html', 
            user=username, 
            all_posts=all_posts, 
            following=following[0:4],
            following_num=len(following),
            following_profile_url=following_profile_url[0:4],
            bio=bio, 
            friend=friend,
            settings_icon=settings_icon, 
            fun_fact=fun_fact, 
            profile_image=profile_image, 
            all_post_times=all_post_times, 
            all_post_urls=all_post_urls, 
            home_icon=home_icon,
            search_icon=search_icon,
            create_icon=create_icon,
            zip=zip, 
            reversed=reversed)
            
    else:
        return render_template("login.html")




@app.route('/user_posts/users/<username2>/posts/<id>', methods=["GET", "POST"])
def post_template(username2=None, id=None):

    try:

        if 'username' in session:
            user = session['username']

            if str(user) == str(username2):
                if is_verified(user) == True:

                    if request.method == 'POST':

                        print("post reached")

                        try:
                            bio = request.form['bio']
                            if bio == "":
                                bio = "Tap here to add a bio!"
                            add_element(user, bio)
                            return redirect(url_for('profile'))
                        except:
                            pass

                        try:
                            fun_fact = request.form['fun_fact']
                            if fun_fact == "":
                                fun_fact = "Tap here to add a fun fact!"
                            update_fun_fact(user, fun_fact)
                            print(fun_fact)
                            return redirect(url_for('profile'))

                        except:
                            pass

                        url3 = f"users/{username2}/posts/{id}"

                   

                        try:
                            delete_post = request.form.get('delete_post')

                            if delete_post == "delete_post":
                                print("delete")
                                remove_post_url(user, url3)
                                print("deleted")
                                return redirect(url_for('profile'))
                        except:
                            pass

                    

                        try:
                            if 'file' not in request.files:
                                return redirect(post)

                            file = request.files['file']
                            # if user does not select file, browser also
                            # submit an empty part without filename
                            if file.filename == '':

                                return redirect(post)

                            if file and allowed_file(file.filename):
                                print("file is allowed profile")
                                username = user
                                file_name_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 30))
                                # this will return a tuple of root and extension
                                split_tup = os.path.splitext(file.filename)
                                # extract the file name and extension
                                file_extension = split_tup[1]
                                file.filename = f"users/{username}_profile_image_{file_name_string}{file_extension}"
                                filename = secure_filename(file.filename)
                                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                print("file saved successfully")
                                print(f" 222222users/{username}/profile_image/{file_name_string}{file_extension} profile")
                                print(f" 11111 users/{username}/profile_image/profile_image/{file_name_string}{file_extension} profile")
                                delete_folder("rustymemories", f"users/{username}/profile_image")
                                print("folder deleted successfully profile")
                                upload_file(f"users/users_{username}_profile_image_{file_name_string}{file_extension}", "rustymemories", f"users/{username}/profile_image/{file_name_string}{file_extension}")
                                print("file uploaded successfully 1 profile")
                                add_profile_image(username, f"users/{username}/profile_image/{file_name_string}{file_extension}")
                                print("file uploaded successfully 2 profile")
                                os.remove(f"users/users_{username}_profile_image_{file_name_string}{file_extension}")
                                return redirect(url_for('profile'))
                        except:
                            pass


                    bio = pull_bio(user)
                    print(f"bio is {bio}")
                    if str(bio) == None or "":
                        bio = "Tap here to add a bio!"

                    fun_fact = pull_fun_fact(user)
                    if str(fun_fact) == None or "":
                        fun_fact = "Tap here to add a fun fact!"

                    all_posts = pull_posts(user)
                    if all_posts == None:
                        all_posts = ["no posts yet"]

                    all_post_times = pull_post_times(user)
                    if all_post_times == None:
                        all_post_times = ["no posts yet"]

                    all_post_urls = pull_post_urls(user)
                    if all_post_urls == None:
                        all_post_urls = ["no posts yet"]

                    print(all_posts)

                    try:
                        profile_image = get_files("rustymemories", f"users/{user}/profile_image")
                        profile_image = profile_image[0]
                    except:
                        if not profile_image:
                            profile_image = "files/profile_basic.png"

                    print(profile_image)

                    together = f"users/{username2}/posts/{id}"

                    row_number = get_row_number(username2, together)

                    all_data = pull_post_info(username2, int(row_number))
                    
                    url = f"users/{username2}/posts/{id}"

                    url2 = f"user_posts/users/{username2}/posts/{id}"


                    settings_icon = 'static/images_home/settings_icon.png'
                    home_icon = 'static/important_images/home_icon.png'
                    search_icon = 'static/important_images/search_icon.png'
                    create_icon = 'static/important_images/create_icon_new.png'


                    
                    following_all = get_followingers(user)

                    following = following_all[0]

                    following_profile_url = following_all[1]
                                


                    return render_template('post_overlay.html', 
                    user=user, 
                    all_posts=all_posts, 
                    bio=bio, 
                    following=following[0:4],
                    following_num=len(following),
                    following_profile_url=following_profile_url[0:4],
                    settings_icon=settings_icon, 
                    fun_fact=fun_fact, 
                    profile_image=profile_image, 
                    all_post_times=all_post_times, 
                    all_post_urls=all_post_urls, 
                    home_icon=home_icon,
                    search_icon=search_icon,
                    create_icon=create_icon, 
                    url=url, 
                    url2=url2,
                    post=together, 
                    username=username2, 
                    all_data=all_data,
                    zip=zip, 
                    reversed=reversed)
                else:
                    return render_template("email_verify.html")
            else:

                if 'username' in session:
                    username3 = session['username']

                    settings_icon = 'static/images_home/settings_icon.png'

                    home_icon = 'static/important_images/home_icon.png'

                    search_icon = 'static/important_images/search_icon.png'

                    create_icon = 'static/important_images/create_icon_new.png'

                    username = username2

                    bio = pull_bio(username)
                    print(f"bio is {bio}")
                    if str(bio) == None or "" or "click to add bio":
                        bio = "This user hasn't added a bio yet!"

                    fun_fact = pull_fun_fact(username)
                    if str(fun_fact) == None or "" or "click to add a fun fact":
                        fun_fact = "This user hasn't added a fun fact yet!"

                    all_posts = pull_posts(username)
                    if all_posts == None:
                        all_posts = ["no posts yet"]

                    all_post_times = pull_post_times(username)
                    if all_post_times == None:
                        all_post_times = ["no posts yet"]

                    all_post_urls = pull_post_urls(username)
                    if all_post_urls == None:
                        all_post_urls = ["no posts yet"]

                    print(all_posts)

                    try:
                        profile_image = get_files("rustymemories", f"users/{username}/profile_image")
                        profile_image = profile_image[0]
                    except:
                        if not profile_image:
                            profile_image = "files/profile_basic.png"

                    print(profile_image)

                    together = f"users/{username}/posts/{id}"

                    row_number = get_row_number(username, together)

                    all_data = pull_post_info(username, int(row_number))
                    
                    url = f"users/{username}/posts/{id}"

                

                    if request.method == "POST":
                            
                        #get value of button clicked

                        print("post request")



                        try:
                            like_button = request.form.get('like_button')

                            if like_button == "like_button":
                                like_post(username3, url, "like_button")
                                print("like")
                        except:
                            pass

                        try:
                            dislike_button = request.form.get('dislike_button')

                            if dislike_button == "dislike_button":
                                like_post(username3, url, "dislike_button")
                                print("dislike")
                        except:
                            pass

                


                    settings_icon = 'static/images_home/settings_icon.png'
                    home_icon = 'static/important_images/home_icon.png'
                    search_icon = 'static/important_images/search_icon.png'
                    create_icon = 'static/important_images/create_icon_new.png'


                    following_all = get_followingers(username)

                    following = following_all[0]

                    following_profile_url = following_all[1]


                    return render_template('post_overlay_public.html', 
                    user=username, 
                    all_posts=all_posts, 
                    bio=bio, 
                    following=following[0:4],
                    following_num=len(following),
                    following_profile_url=following_profile_url[0:4],
                    settings_icon=settings_icon, 
                    fun_fact=fun_fact, 
                    profile_image=profile_image, 
                    all_post_times=all_post_times, 
                    all_post_urls=all_post_urls, 
                    home_icon=home_icon,
                    search_icon=search_icon,
                    create_icon=create_icon, 
                    url=url, 
                    post=together, 
                    username=username, 
                    all_data=all_data,
                    zip=zip, 
                    reversed=reversed)
                    
        else:
            return render_template("login.html")
    except:
        return redirect(url_for('profile'))





@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404



if __name__ == "__main__":
	app.run(host='127.0.0.1', port=5540, debug=True, threaded=True)