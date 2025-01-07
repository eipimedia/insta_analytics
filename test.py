from flask import Flask, request, jsonify
import os
import pandas as pd
import requests
import json
import time

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define headers for the Instagram API
headers = {
    "authority": "i.instagram.com",
    "accept": "/",
    "accept-language": "en-US,en;q=0.9,hi;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": 'YOUR_COOKIE_HERE',
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "x-ig-app-id": "936619743392459",
}

# Define the POST API endpoint
post_url = "https://hook.eu2.make.com/6asghw6bevroa8fapd9devh4sobqd5p9"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return process_csv(file_path)

    return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400


def process_csv(file_path):
    # Load the CSV file
    data = pd.read_csv(file_path)

    # Extract usernames
    usernames = data["Username"].tolist()

    # Initialize a dictionary to store data for all usernames
    all_data = {}

    # Process each username
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
                all_data[username] = {
                    "totalLikes": total_likes,
                    "totalViews": total_views,
                    "totalComments": total_comments,
                    "avgLikes": avg_likes,
                    "avgViews": avg_views,
                    "avgComments": avg_comments,
                    "avgEngagement": avg_engagement,
                }
                break
            except requests.exceptions.RequestException as e:
                retries -= 1
                print(f"Retrying for {username}: {e}")
                time.sleep(2)
            except KeyError as e:
                print(f"Data format error for {username}: Missing key {e}")
                all_data[username] = {"error": f"Missing key {e}"}
                break
        else:
            all_data[username] = {"error": "Failed after retries"}

    # Save results
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'IG_Usernames_Responses.json')
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)

    # Send data to the POST API
    try:
        post_response = requests.post(post_url, json=all_data)
        if post_response.status_code == 200:
            return jsonify({"message": "Data successfully sent to the POST endpoint.", "results": all_data}), 200
        else:
            return jsonify({"error": "Failed to send data to POST endpoint.", "details": post_response.text}), 500
    except Exception as e:
        return jsonify({"error": "Error sending data to POST endpoint.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
