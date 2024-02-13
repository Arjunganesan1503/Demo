# Importing necessary libraries
import urllib.parse
import pymongo
import mysql.connector
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from pymongo import MongoClient
from googleapiclient.errors import HttpError
from datetime import datetime

# Define channel IDs
Raaj_Kamal_Films_International = "UC_gXhnzeF5_XIFn4gx_bocg"
Vlog_Thamila = "UC2NRNwMK1btrEJnwpVqa7ZA"
FeelFreetoLearn_தமிழ் = "UCxel-aNEfxk1s8dWy97C_DQ"
JD_Cinemas = "UCQExh9iPxZ1YkgnZANbyMNw"
Un_Signed = "UCXnDDUQyJpRfC98_ZRIuhZA"
Touring_Talkies = "UC5Va8SDMp-yviytKMh9YaNQ"
GP_Express = "UCK94kFOQblF8sK66O7gKW8Q"
GP_bro = "UCECs0V4X69ZbDolwK-g8wHg"
Hobby_Explorer_Tamil = "UCYqXh1HzJSYYYmbaoK4veDw"
Social_Talkies = "UCjOT5dLJUc60HFJiphmFh1g"


channel_ids = [
    Raaj_Kamal_Films_International,
    Vlog_Thamila,
    FeelFreetoLearn_தமிழ்,
    JD_Cinemas,
    Un_Signed,
    Touring_Talkies,
    GP_Express,
    GP_bro,
    Hobby_Explorer_Tamil,
    Social_Talkies
]

# API information
API_KEY = "AIzaSyADE9RgL7jhrwq3Qb7b_LEHXwI5OPUDkRY"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# MongoDB connection
def connect_mongodb():
    try:
        username = urllib.parse.quote_plus('arjunkamal21')
        password = urllib.parse.quote_plus('9952849476Aa1503')
        dbname = 'Youtube_harvesting'
        cluster_url = 'cluster0.sgnyps0.mongodb.net'
        uri = f"mongodb+srv://{username}:{password}@{cluster_url}/{dbname}?retryWrites=true&w=majority"
        dbname = '<your_database_name>'
        client = MongoClient(uri)
        print("Connected to Mongodb database successfully!")
        return client["Youtube_harvesting"]
    except pymongo.errors.ConnectionFailure as e:
        print(f"Error connecting to Mongodb database: {e}")
        return None
    
# MySQL connection
def connect_mysql():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="9952849476Aa@",
            database="project",
            auth_plugin='mysql_native_password',
            charset='utf8mb4'
        )
        print("Connected to MySQL database successfully!")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# Connect to YouTube API
def connect_youtube_api():
    youtube =  build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
    return youtube

# Get playlist ID
def get_playlist_info(youtube, channel_id):
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    
    # Check if the response contains any items
    items = response.get("items", [])
    if items:
        return items[0].get("contentDetails", {}).get("relatedPlaylists", {})
    else:
        print("No playlist information found for channel ID:", channel_id)
        return {}

# Get comment information for a given list of video IDs
def get_comment_info(youtube, video_ids):
    comments = []
    for video_id in video_ids:
        try:
            next_page_token = None
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50,
                pageToken= next_page_token
            )
            response = request.execute()
            for item in response.get("items", []):
                comment_data = item["snippet"]["topLevelComment"]["snippet"]
                Comment_dtime = datetime.strptime(comment_data["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                comment_info = {
                    "Comment_Id": item["id"],
                    "Video_Id"  : video_id,
                    "Comment_Text": comment_data["textDisplay"],
                    "Comment_Author": comment_data["authorDisplayName"],
                    "Comment_PublishedAt": Comment_dtime
                }
                comments.append(comment_info)
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except HttpError as e:
            if e.resp.status == 403:
                # for disabled comments
                print(f"Comments are disabled for video with ID {video_id}")
            else:
                # Handle other HTTP errors
                print("Error fetching comments:", e)
    return comments

# Fetch channel information from YouTube API
def get_channel_info(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    # Check if the response contains any items
    if 'items' in response and len(response['items']) > 0:
        channel_data = response['items'][0]

        channel_info = {
            "Channel_Name": channel_data["snippet"]["title"],
            "Channel_Id": channel_id,
            "Subscription_Count": int(channel_data["statistics"]["subscriberCount"]),
            "Channel_Views": int(channel_data["statistics"]["viewCount"]),
            "Channel_Description": channel_data["snippet"]["description"],
            "Playlist_Id": get_playlist_info(youtube, channel_id).get("uploads"),
            "Total_Videos":int(channel_data["statistics"]["videoCount"])
        }
        return channel_info
    else:
        print("No channel information found for channel ID:", channel_id)
        return None

# Fetch video information from YouTube API
def get_video_info(youtube, playlist_id):
    videos = []

    if not playlist_id:
        print("Error: Missing playlist ID.")
        return videos  # if the playlist_id it returns empty list

    try:
        next_page_token = None
        while True:
            request = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            # Check if the response contains 'items' key
            if 'items' not in response:
                break

            for item in response['items']:
                video_data = item['snippet']
                video_id = video_data['resourceId']['videoId']
                video_details = youtube.videos().list(
                    part="statistics,contentDetails,snippet",
                    id=video_id
                ).execute()
                statistics = video_details['items'][0]['statistics']
                channel_id = video_details['items'][0]['snippet']['channelId']
                video_duration = video_details['items'][0]['contentDetails'].get('duration', 'Not Available')
                comment_info = get_comment_info(youtube, [video_id])  # Extract comments
                video_dtime = datetime.strptime(video_data["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                comments_text = [comment['Comment_Text'] for comment in comment_info]

                video_info = {
                    "Video_Id": video_id,
                    "Video_Name": video_data["title"],
                    "Channel_Id" : channel_id,
                    "Video_Description": video_data["description"],
                    "Tags": video_data.get("tags", []),
                    "PublishedAt": video_dtime,
                    "View_Count": int(statistics.get("viewCount", 0)),
                    "Like_Count": int(statistics.get("likeCount", 0)),
                    "Dislike_Count": int(statistics.get("dislikeCount", 0)),
                    "Comment_Count": int(statistics.get("commentCount", 0)),
                    "Duration": video_duration[2:],  # Remove "PT" from duration
                    "Thumbnail": video_data["thumbnails"]["default"]["url"],
                    "Caption_Status": item['contentDetails'].get('caption', 'Not Available'),
                    "Comments": comments_text
                }
                videos.append(video_info)
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

    except HttpError as e:
        if e.resp.status == 400:
            print("Error: Missing required parameter. Please check the playlist ID.")
        else:
            print(f"An error occurred: {e}")

    return videos


# Create tables and insert data into MySQL
def create_tables_mysql(cursor, connection):
    try:
        # Create channels table
        cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
                        Channel_Name VARCHAR(100),
                        Channel_Id VARCHAR(80) PRIMARY KEY, 
                        Subscription_Count BIGINT, 
                        Views BIGINT,
                        Total_Videos INT,
                        Channel_Description TEXT,
                        Playlist_Id VARCHAR(50)
                    )''')

        # Create playlists table
        cursor.execute('''CREATE TABLE IF NOT EXISTS playlists (
                        Playlist_Id VARCHAR(50) PRIMARY KEY
                    )''')

        # Create videos table
        cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                        Video_Id VARCHAR(50) PRIMARY KEY,
                        Video_Name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                        Channel_Id VARCHAR(80),
                        PublishedAt DATETIME,
                        View_Count BIGINT,
                        Like_Count BIGINT,
                        Dislike_Count BIGINT,
                        Comment_Count BIGINT,
                        Duration VARCHAR(20),
                        Thumbnail VARCHAR(255),
                        Caption_Status VARCHAR(20)
                    )''')
        # Create comments table
        cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                        Comment_Id VARCHAR(50) PRIMARY KEY,
                        Video_Id VARCHAR(50),
                        Comment_Text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                        Comment_Author VARCHAR(100),
                        Comment_PublishedAt DATETIME
                    )''')    
            
        connection.commit()  # Commit the transaction
        return True
    except mysql.connector.Error as e:
        print(f"Error executing MySQL query: {e}")
        return False

# Function to collect and store data for a selected channel
def collect_and_store_data(selected_channel_name, channel_info):
    try:
        # Connect to YouTube API
        youtube = connect_youtube_api()

        # Get the channel ID for the selected channel name
        channel_id = None
        for key, value in channel_info.items():
            if value == selected_channel_name:
                channel_id = key
                break

        if channel_id is None:
            print(f"Error: Channel ID not found for channel '{selected_channel_name}'")
            return None  
        
        # Get channel information
        channel_info_data = get_channel_info(youtube, channel_id)

        # Get playlist information
        playlist_info = get_playlist_info(youtube, channel_id)
        uploads_playlist_id = playlist_info.get("uploads")  # "uploads" is the key for the playlist ID

        # Get video information
        videos = []
        if uploads_playlist_id:
            videos.extend(get_video_info(youtube, uploads_playlist_id))
        # Get comment information
        comments = []            
        for video in videos:
            comments.extend(get_comment_info(youtube, [video["Video_Id"]]))

        # Store the collected data in MongoDB
        db = connect_mongodb()
        if db is not None:
            # Store channel information
            db.channels.insert_one(channel_info_data)

            # Store playlist information
            if uploads_playlist_id:
                db.playlists.insert_one({"Playlist_Id": uploads_playlist_id})

            # Store video information
            for video in videos:
                db.videos.insert_one(video)

            # Store comment information
            for comment in comments:
                db.comments.insert_one(comment)                

            collected_data = {
                'channels': channel_info_data,
                'playlists': playlist_info,
                'videos': videos,
                'comments': comments
            }    
            return collected_data

        else:
            print('Failed to connect to MongoDB or the database object is None.')
            return None  

    except Exception as e:
        error_message = f'Error occurred: {str(e)}'
        print(error_message)
        return None  


# Define function to migrate data from MongoDB to MySQL
def migrate_data_to_sql(selected_channel_name, channel_info):
    try:
        # Find the channel ID for the selected channel name
        channel_id = None
        for key, value in channel_info.items():
            if value == selected_channel_name:
                channel_id = key
                break
        if channel_id:
            # Connect to MongoDB
            db = connect_mongodb()
            if db is not None:  
                # Fetch data for the selected channel from MongoDB
                channel_info_db = db.channels.find_one({"Channel_Name": selected_channel_name})

                if channel_info_db is not None:
                    playlist_info = db.playlists.find_one({"Playlist_Id": channel_info_db.get("Playlist_Id")})
                    videos = db.videos.find({"Channel_Id": channel_info_db.get("Channel_Id")})
                    video_list = list(videos)
                    all_comments = []  # all comments in a list

                    for video in video_list:
                        video_id = video.get("Video_Id")
                        comments = db.comments.find({"Video_Id": video_id})
                        video_comments = []
                        for comment in comments:
                            video_comments.append(comment)
                        all_comments.append({video_id: video_comments})
                    
                    # Connect to MySQL
                    connection = connect_mysql()
                    if connection is not None:  
                        cursor = connection.cursor()

                        # Create tables in MySQL
                        if create_tables_mysql(cursor, connection):  
                            print("Tables created successfully.")
                        else:
                            print("Failed to create tables.")                            
                        
                        # Migrate channel information to MySQL
                        cursor.execute('''INSERT IGNORE INTO channels (Channel_Name, Channel_Id, Subscription_Count, Views, Total_Videos,
                                            Channel_Description, Playlist_Id) VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                                        (channel_info_db.get("Channel_Name"), channel_info_db.get("Channel_Id"),
                                        channel_info_db.get("Subscription_Count"), channel_info_db.get("Channel_Views"),
                                        channel_info_db.get("Total_Videos"), channel_info_db.get("Channel_Description"),
                                        playlist_info.get('Playlist_Id')))
                        
                        # Migrate playlist information to MySQL
                        cursor.execute('''INSERT IGNORE INTO playlists (Playlist_Id) VALUES (%s)''', (playlist_info.get('Playlist_Id'),))
                        print("Playlist information migrated to MySQL")  # Print confirmation message

                        # Migrate video information to MySQL
                    for video in video_list:
                        try:
                            cursor.execute('''INSERT IGNORE INTO videos (Video_Id, Video_Name, Channel_Id, PublishedAt, View_Count,
                                        Like_Count, Dislike_Count, Comment_Count, Duration, Thumbnail, Caption_Status) VALUES
                                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                        (video["Video_Id"], video["Video_Name"], video["Channel_Id"], video["PublishedAt"],
                                        video["View_Count"], video["Like_Count"], video["Dislike_Count"],
                                        video["Comment_Count"], video["Duration"], video["Thumbnail"], video["Caption_Status"]))

                        except Exception:
                         print("failed to insert")

                    connection.commit()     

                       # Migrate comments information to MySQL
                    for video_comments in all_comments:
                        video_id, comments = list(video_comments.items())[0]  # Extract video_id and comments
                        for comment in comments:
                            cursor.execute('''INSERT IGNORE INTO comments (Comment_Id, Video_Id, Comment_Text, Comment_Author, Comment_PublishedAt) VALUES
                                            (%s, %s, %s, %s, %s)''',
                                            (comment["Comment_Id"], video_id, comment["Comment_Text"], 
                                            comment["Comment_Author"], comment["Comment_PublishedAt"]))
                    print("Comments information migrated to MySQL")  # Print confirmation message   

                    connection.commit()  
                    cursor.close()
                    connection.close()
                    return True, 'Data migrated to SQL successfully!'
 
                else:
                    return False, f'No data found for channel: {selected_channel_name}'
            else:
                return False, 'Failed to connect to MongoDB database.'
        else:
            return False, 'Failed to find selected channel ID.'
    except Exception as e:
        return False, str(e)


# Function to answer questions based on SQL data
def answer_question_from_sql(question):
    try:
        # Connect to MySQL
        connection = connect_mysql()
        if connection:
            cursor = connection.cursor()

            # Answering questions based on MySQL data
            if question == 'All the videos and the Channel Name':
                cursor.execute("SELECT videos.Video_Name, channels.Channel_Name FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Video Name", "Channel Name"])
                return df

            elif question == 'Channels with most number of videos':
                cursor.execute("SELECT Channel_Name, COUNT(*) AS Video_Count FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id GROUP BY Channel_Name ORDER BY Video_Count DESC")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Channel Name", "Number of Videos"])
                return df

            elif question == '10 most viewed videos':
                cursor.execute("SELECT Video_Name, View_Count, Channel_Name FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id ORDER BY View_Count DESC LIMIT 10")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Video Name", "View Count", "Channel Name"])
                return df

            elif question == 'Comments in each video':
                cursor.execute("SELECT Video_Name, Comment_Count FROM videos")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Video Name", "Comment Count"])
                return df

            elif question == 'Videos with highest likes':
                cursor.execute("SELECT Video_Name, Like_Count, Channel_Name FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id ORDER BY Like_Count DESC LIMIT 10")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Video Name", "Like Count", "Channel Name"])
                return df

            elif question == 'Total number of likes and dislikes for each video':
                cursor.execute("SELECT Video_Name, Like_Count, Dislike_Count FROM videos")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Video Name", "Like Count", "Dislike Count"])
                return df

            elif question == 'Total number of views for each channel':
                cursor.execute("SELECT Channel_Name, SUM(View_Count) AS Total_Views FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id GROUP BY Channel_Name")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Channel Name", "Total Views"])
                return df

            elif question == 'Names of all the channels that have published videos in the year 2022':
                cursor.execute("SELECT DISTINCT Channel_Name FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id WHERE YEAR(PublishedAt) = 2022")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Channel Name"])
                return df

            elif question == 'Average duration of all videos in each channel':
                cursor.execute("SELECT Channel_Name, AVG(Duration) AS Average_Duration FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id GROUP BY Channel_Name")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Channel Name", "Average Duration"])
                return df
            
            elif question == 'Videos with the highest number of comments':
                cursor.execute("SELECT Video_Name, Comment_Count, Channel_Name FROM videos JOIN channels ON videos.Channel_Id = channels.Channel_Id ORDER BY Comment_Count DESC LIMIT 10")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=["Video Name", "Comment Count", "Channel Name"])
                return df
            
              
            cursor.close()
            connection.close()
        else:
            st.error('Failed to connect to MySQL database.')

    except mysql.connector.Error as e:
        st.error(f'MySQL Error: {str(e)}')
    except Exception as e:
        st.error(f'Error: {str(e)}')

# Streamlit user interface
def main():

    st.sidebar.title("YOUTUBE DATA HARVESTING AND WAREHOUSING")
    st.sidebar.header("SKILL TAKE AWAY")
    st.sidebar.caption('Python scripting')
    st.sidebar.caption("Data Collection")
    st.sidebar.caption("MongoDB")
    st.sidebar.caption("Streamlit")
    st.sidebar.caption("API Integration")
    st.sidebar.caption("Data Management using MongoDB and SQL")

    # Define channel IDs and corresponding channel names
    channel_info = {
        "UC_gXhnzeF5_XIFn4gx_bocg": "Raaj Kamal Films International",
        "UC2NRNwMK1btrEJnwpVqa7ZA": "Vlog Thamila",
        "UCxel-aNEfxk1s8dWy97C_DQ": "FeelFreetoLearn_தமிழ்",
        "UCQExh9iPxZ1YkgnZANbyMNw": "JD Cinemas",
        "UCXnDDUQyJpRfC98_ZRIuhZA": "Un Signed",
        "UC5Va8SDMp-yviytKMh9YaNQ": "Touring Talkies",
        "UCK94kFOQblF8sK66O7gKW8Q": "GP Express",
        "UCECs0V4X69ZbDolwK-g8wHg": "GP bro",
        "UCYqXh1HzJSYYYmbaoK4veDw": "Hobby Explorer Tamil",
        "UCjOT5dLJUc60HFJiphmFh1g": "Social Talkies"
    }

    # Step 1: Add a dropdown menu to select the channel name
    selected_channel_name = st.selectbox("Select Channel", list(channel_info.values()))
    
# Step 2: Collect and store data for the selected channel
    if st.button("Collect and Store data"):
        with st.spinner('Collecting and storing data...'):
            # Get the channel ID for the selected channel name
            selected_channel_id = next((key for key, value in channel_info.items() if value == selected_channel_name), None)
            if selected_channel_id:
                collect_and_store_data(selected_channel_name, channel_info)  # Pass channel_info dictionary
                st.success('Data collected and stored successfully!')           
            else:
                print("error collection")

    # Step 3: Migrate collected data to SQL
    if st.button("Migrate to SQL"):
        with st.spinner('Migrating data to SQL...'):            
            # Get the information of the selected channel
            selected_channel_id = next((key for key, value in channel_info.items() if value == selected_channel_name), None)
            if selected_channel_id:
                # Call migrate_data_to_sql function with the selected channel name and channel info
                migration_status, migration_message = migrate_data_to_sql(selected_channel_name, channel_info)
                migrate_data_to_sql(selected_channel_name, channel_info)
                if migration_status:                
                 st.success(migration_message)
            else:
                st.error(f'Migration failed: {migration_message}')
   
    # Step 4: Answer question
    questions = [
        "All the videos and the Channel Name",
        "Channels with most number of videos",
        "10 most viewed videos",
        "Comments in each video",
        "Videos with highest likes",
        "Total number of likes and dislikes for each video",
        "Total number of views for each channel",
        "Names of all the channels that have published videos in the year 2022",
        "Average duration of all videos in each channel",
        "Videos with the highest number of comments"
    ]

    selected_question = st.selectbox("Select Question", questions)

    if st.button("Submit"):
        with st.spinner('Fetching answers...'):
            result_df = answer_question_from_sql(selected_question)
            if result_df is not None:
                st.dataframe(result_df)
            else:
                st.warning('No answer found.')


if __name__ == "__main__":
    main()
