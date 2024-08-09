from flask import render_template, redirect, url_for, request, jsonify
from app import app
from app.videos import Videos
from app.db import Db

video = Videos()
db = Db()



@app.route('/')      
@app.route('/index', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        search = request.form['search']
        if search[0] == '#':
            does_hashtag_exist = db.hashtag_exists(search)

            if does_hashtag_exist is False:
                return redirect(url_for('index')) 
            else:
                feed, hashtags = db.posts(search_hashtag=search)
                return render_template('index.html',feed=feed,hashtags=hashtags)
                  
                        
        if search[0] == '@':
            profiles = db.user_exists(search)
            if profiles:                          
                return redirect(url_for('profile')) 
            else:
                return redirect(url_for('index'))
            
        video.search(search)
        return redirect(url_for('videos')) 

    feed, hashtags = db.posts()                    
    return render_template('index.html',feed=feed,hashtags=hashtags)

@app.route('/likes', methods=['POST'])
def likes():
    if request.method == 'POST':
        post_id = request.json['post_id']
    db.like(post_id)
    return ''


@app.route('/message', methods = ['GET', 'POST'])
def message():
    return render_template('message.html')

@app.route('/post', methods = ['GET', 'POST'])
def post():
    if request.method == 'POST':
        tweet = request.form.get('tweet')
        img_file = request.files.get('file')
        successful = db.upload(tweet=tweet, image_file=img_file)

        if successful:
            return redirect(url_for('profile'))
    return render_template('post.html')

@app.route('/profile')
def profile():
    user_info,followers, following, feed,hashtags = db.load_profile()  
    username, name , bio = user_info[:3]
    
    return render_template('profile.html',username=username,name=name
                           ,bio=bio, followers=followers,following=following,feed=feed,hashtags=hashtags)

@app.route('/followers', methods = ['GET', 'POST'])
def followers():
    #when press follow button
    if request.method == 'POST':
        if 'follow' in request.form:
            target_user = request.form['follow']
            db.follow(target_user)

        elif 'unfollow' in request.form:
            target_user = request.form['unfollow']
            db.unfollow(target_user)
        
     
    #display follower list
    followers_list, mutual= db.get_followers()
    return render_template('followers.html',followers_list=followers_list, mutual=mutual)

@app.route('/following', methods = ['GET', 'POST'])
def following():
    #when press follow button
    if request.method == 'POST':
        if 'follow' in request.form:
            target_user = request.form['follow']
            db.follow(target_user)

        elif 'unfollow' in request.form:
            target_user = request.form['unfollow']
            db.unfollow(target_user)

    #display following list
    following_list, mutual = db.get_following()
    return render_template('following.html',following_list=following_list,mutual=mutual)


@app.route('/video', methods = ['GET', 'POST'])
def videos():

    if request.method == 'POST':           
        if 'next' in request.form:
            link, video_index, page = video.search('next')
            return render_template('videos.html', link=link,video_index=video_index,page=page)
        
        elif 'back' in request.form:
            link, video_index, page = video.search('back')
            return render_template('videos.html', link=link,video_index=video_index,page=page)
        
    else:
        link, video_index, page = video.search('none')
        return render_template('videos.html',link=link,video_index=video_index,page=page)






 
















