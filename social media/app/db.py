import sqlite3
from PIL import Image
import os
from . import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from werkzeug.utils import secure_filename

class Db:

    def __init__(self):            #debug     
        self.username = '@user2'   #profile
        self.user = '@user1'       #logged in as 
        
    #                                     DEBUG
    def loggedin(self):
        self.user = '@user1' 
    
    def like(self, post_id):
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Likes WHERE PostID=? AND Username=?",(post_id,self.user))
            liked = cursor.fetchone()

            if liked is None:
                cursor.execute("INSERT INTO Likes (PostID,Username) VALUES (?,?)",(post_id,self.user))
                conn.commit()
            else:
                cursor.execute("DELETE FROM Likes WHERE PostID=? AND Username=?",(post_id,self.user))
                conn.commit()

    def user_already_following(self,follows_list):
        mutual = []
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT target FROM follows WHERE stalker=?", (self.user,))
            user_follows = cursor.fetchall()
    
        for follower in follows_list:
            found = False
            for user_follow in user_follows:
                if follower[0] == user_follow[0]:
                    found = True
                    break
            if found:
                mutual.append(follower)
        
        return mutual

    def follow(self, target_user):
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO follows (stalker,target) VALUES (?,?)", (self.user, target_user))
            conn.commit()

    def unfollow(self, target_user):
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM follows WHERE stalker=? AND target=?",(self.user,target_user))
            conn.commit()

    def load_profile(self):
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Username, Name, Bio FROM User WHERE Username=?", (self.username,))
            user_info = cursor.fetchone()  #tuple
            cursor.execute("SELECT COUNT(stalker) FROM Follows WHERE target=?", (self.username,))
            followers = cursor.fetchall()
            cursor.execute("SELECT COUNT(target) FROM Follows WHERE stalker=?", (self.username,))
            follows = cursor.fetchall()
        
        posts, sidebar_hashtags = self.posts(self.username)

        return user_info[:3], followers[0][0], follows[0][0],posts, sidebar_hashtags
    
    def get_followers(self): 
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT follows.stalker, User.Name, User.bio  
                           FROM follows
                           LEFT JOIN User ON follows.stalker = User.Username
                           WHERE target=?""", (self.username,))
            follower = cursor.fetchall()   
            
        mutual = self.user_already_following(follower)

        return follower, mutual

    def get_following(self):
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT follows.target, User.Name, User.bio  
                           FROM follows
                           LEFT JOIN User ON follows.target = User.Username
                           WHERE stalker=?""", (self.username,))
            following = cursor.fetchall()   
            
        mutual = self.user_already_following(following)

        return following, mutual
    
    def posts(self,user=None,search_hashtag=None):

        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            base_query = """
                SELECT 
    Post.PostID,
    Post.Username, 
    User.Name, 
    Post.Content, 
    Post.Image, 
    Post.Timestamp,
    (SELECT COUNT(*) FROM Likes WHERE Likes.PostID = Post.PostID) AS LikeCount,
    (SELECT GROUP_CONCAT(Hashtag.Hashtag, ' ') FROM Hashtag WHERE Hashtag.PostID = Post.PostID) AS Hashtags,
    (SELECT COUNT(*) FROM Comment WHERE Comment.PostID = Post.PostID) AS CommentCount,
    (SELECT LikeID FROM Likes WHERE Likes.PostID = Post.PostID AND likes.username=?) AS IfLiked
FROM 
    Post
LEFT JOIN 
    User ON Post.Username = User.Username
            """
            #loads posts for user only
            if user:
                query = f"{base_query} WHERE Post.Username = ? ORDER BY Post.Timestamp DESC;"
                cursor.execute(query, (self.user,user))
            #loads posts for hashtags only
            elif search_hashtag:
                query = f'''{base_query} WHERE Post.PostID IN
                (SELECT PostID FROM Hashtag WHERE Hashtag = ?)
                ORDER BY Post.Timestamp DESC;'''
                cursor.execute(query, (self.user,search_hashtag))
            #loads posts for index
            else:
                query = f"{base_query} ORDER BY Post.Timestamp DESC;"
                cursor.execute(query, (self.user,))

            post_info = cursor.fetchall()

            #gets sidebar hashtags array
            cursor = conn.cursor()
            cursor.execute("SELECT Hashtag, Timestamp FROM Hashtag LIMIT 6")
            sidebar_hashtags = cursor.fetchall()                

        #formats timestamp
        for i in range(len(post_info)):
            post = list(post_info[i])
            del post_info[i]
            formated_date = post[5][:10]
            post[5] = formated_date
            post_info.insert(i,post) 
            #formats hashtags in posts
            if post[7] == None:
                post[7] = ''

        #formats time stamp in Sidebar hashtags List 
        for i in range(6):
            sidebar_hashtag = list(sidebar_hashtags[i])
            del sidebar_hashtags[i]
            formated_date = sidebar_hashtag[1][:10]
            sidebar_hashtag[1] = formated_date
            sidebar_hashtags.insert(i,sidebar_hashtag)

        return post_info, sidebar_hashtags 


     #test this
    def get_comments(self, postId): 
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Content, Username, Timestamp FROM Comment WHERE PostID=?", (postId,))
            comment_info = cursor.fetchall()

        return comment_info


    def user_exists(self, username):
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT Username FROM User WHERE Username='{username}'")
            user = cursor.fetchone()  

        if user is None:
            return False
        else:
            self.username = user[0]
            return True
    
    def hashtag_exists(self, search):
        with sqlite3.connect('social media.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT Hashtag FROM Hashtag WHERE Hashtag='{search}'")
            hashtag = cursor.fetchone()
        
        if hashtag is None:
            return False
        else:
            return True

    def create_user(self):
        pass
        #ADD AN @ INFORT OF USERNAME
        #create default pfp
    
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def upload(self, tweet, image_file):

        if image_file and self.allowed_file(image_file.filename) and tweet:
            
            with sqlite3.connect('social media.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM Post WHERE Username=?',(self.user,))
                post_rank = cursor.fetchone()[0] + 1
                postId = self.user + '_' + str(post_rank)

                img = Image.open(image_file)
                filename = postId + '.png'
                img.save(os.path.join(UPLOAD_FOLDER, filename), 'PNG')

                cursor.execute("INSERT INTO Post (PostID,Username,Content,Image) VALUES (?,?,?,?)", (postId,self.user,tweet,1))
                conn.commit()
            return True

            
        elif tweet:
            with sqlite3.connect('social media.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM Post WHERE Username=?',(self.user,))
                post_rank = cursor.fetchone()[0] + 1
                postId = self.user + '_' + str(post_rank)

                cursor.execute("INSERT INTO Post (PostID,Username,Content,Image) VALUES (?,?,?,?)", (postId,self.user,tweet,0))
                conn.commit()
            return True
        
        else:
            return False

# db = Db()
# db.posts()
# post ,h= db.posts()
# print(post)


# # ['@user1_4', '@user1', 'User One', '4th content posted', 1, '2024-07-05', 0, '#ski', 0, None]