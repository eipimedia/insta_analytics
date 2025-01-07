import requests
import pandas as pd
import time
import json

# Define the headers for the Instagram API
headers = {
    "authority": "i.instagram.com",
    "accept": "/",
    "accept-language": "en-US,en;q=0.9,hi;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": 'ig_did=4F8F57CA-BF49-4B85-8C52-611B0F525ACB; datr=dPE1Zc5Ddn8P6Q-xSRlNIMgG; ig_nrcb=1; ds_user_id=45032874760; ps_n=0; ps_l=0; mid=ZbqF0AAEAAHkroAy-X6KDIIhEDoQ; csrftoken=iBZmKJWoMnM6dEZhsp3JiS6ssjxq5MDQ;',
    "sec-ch-ua": '"Chromium";v="122", "Not(A)";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "none",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "x-asbd-id": "198387",
    "x-csrftoken": "iBZmKJWoMnM6dEZhsp3JiS6ssjxq5MDQ",
    "x-ig-app-id": "936619743392459",
    "x-ig-www-claim": "hmac.AR1yCz586xi6ZoH24dmvdq_ckLvj3lmcN1JbVTnAPHMcnl73",
    "x-instagram-ajax": "1",
    "x-requested-with": "XMLHttpRequest",
}

# Define the POST API endpoint
post_url = "https://hook.eu2.make.com/6asghw6bevroa8fapd9devh4sobqd5p9"

# Load the CSV file
file_path = './IG_Usernames.csv'
data = pd.read_csv(file_path)

# Extract usernames from the CSV
usernames = data["Username"].tolist()

# List to store all responses
all_responses = []

# Process each username with retry logic
for username in usernames:
    print(f"Processing username: {username}")
    instagram_url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    retries = 3
    while retries > 0:
        try:
            response = requests.get(instagram_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            
            # Extract relevant data
            followers_count = data["data"]["user"]["edge_followed_by"]["count"]
            posts = data["data"]["user"]["edge_felix_video_timeline"]["edges"]

            total_likes = sum(post["node"].get("edge_liked_by", {}).get("count", 0) for post in posts)
            total_views = sum(post["node"].get("video_view_count", 0) for post in posts)
            total_comments = sum(post["node"].get("edge_media_to_comment", {}).get("count", 0) for post in posts)
            post_count = len(posts)

            avg_likes = total_likes / post_count if post_count > 0 else 0
            avg_views = total_views / post_count if post_count > 0 else 0
            avg_comments = total_comments / post_count if post_count > 0 else 0
            avg_engagement = (avg_likes + avg_views + avg_comments) / followers_count if followers_count > 0 else 0

            # Store the aggregated data
            all_responses.append({
                "username": username,
                "totalLikes": total_likes,
                "totalViews": total_views,
                "totalComments": total_comments,
                "avgLikes": avg_likes,
                "avgViews": avg_views,
                "avgComments": avg_comments,
                "avgEngagement": avg_engagement,
            })
            break  # Exit the retry loop on success
        except requests.exceptions.RequestException as e:
            retries -= 1
            print(f"Retrying for {username}: {e}")
            time.sleep(2)  # Wait before retrying
        except KeyError as e:
            print(f"Data format error for {username}: Missing key {e}")
            all_responses.append({"username": username, "error": f"Missing key {e}"})
            break
    else:
        # Append error if all retries fail
        all_responses.append({"username": username, "error": "Failed after retries"})

# Save all responses to a JSON file
output_file = "./IG_Usernames_Responses.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(all_responses, json_file, ensure_ascii=False, indent=4)

print(f"All responses have been saved to {output_file}")

# Send the entire JSON file's data to the POST API
try:
    with open(output_file, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    
    # Send the data to the POST API
    post_response = requests.post(post_url, json=json_data)
    if post_response.status_code == 200:
        print("Entire JSON data successfully sent to the POST endpoint.")
    else:
        print(f"Failed to send JSON data. HTTP Status Code: {post_response.status_code}")
        print(post_response.text)

except Exception as e:
    print(f"Error sending JSON data: {e}")
