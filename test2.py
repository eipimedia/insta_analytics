import requests

# Define the Instagram API endpoint and headers
instagram_url = "https://i.instagram.com/api/v1/users/web_profile_info/?username=rohitreddygoa"
headers = {
    "authority": "i.instagram.com",
    "accept": "/",
    "accept-language": "en-US,en;q=0.9,hi;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": 'ig_did=4F8F57CA-BF49-4B85-8C52-611B0F525ACB; datr=dPE1Zc5Ddn8P6Q-xSRlNIMgG; ig_nrcb=1; ds_user_id=45032874760; ps_n=0; ps_l=0; mid=ZbqF0AAEAAHkroAy-X6KDIIhEDoQ; csrftoken=iBZmKJWoMnM6dEZhsp3JiS6ssjxq5MDQ; shbid="8503\\05445032874760\\0541741773742:01f7031d590a0902f9cc558f4016652ca4375b7b09a433547d9c7639e765399fa2195d60"; shbts="1710237742\\05445032874760\\0541741773742:01f70fb21741748081c033e6c761ef73a7f73432a9cac667babc7c7f35a66fac1b1c22bb"; rur="NAO\\05445032874760\\0541741773914:01f7c8c343f2aac7691a16e0b705b714253744eebe5b8caad15c902cae2dba7fc7fff837"; csrftoken=iBZmKJWoMnM6dEZhsp3JiS6ssjxq5MDQ',
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

# Fetch data from the Instagram API
response = requests.get(instagram_url, headers=headers)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()

    # Extract followers, views, likes, and comments
    followers_count = data["data"]["user"]["edge_followed_by"]["count"]
    posts = data["data"]["user"]["edge_felix_video_timeline"]["edges"]

    total_likes = 0
    total_views = 0
    total_comments = 0
    post_count = len(posts)

    for post in posts:
        node = post["node"]
        total_likes += node.get("edge_liked_by", {}).get("count", 0)
        total_views += node.get("video_view_count", 0)  # Default to 0 if not present
        total_comments += node.get("edge_media_to_comment", {}).get("count", 0)

    # Calculate averages
    avg_likes = total_likes / post_count if post_count > 0 else 0
    avg_views = total_views / post_count if post_count > 0 else 0
    avg_comments = total_comments / post_count if post_count > 0 else 0

    # Calculate average engagement rate
    avg_engagement = (avg_likes + avg_views + avg_comments) / followers_count if followers_count > 0 else 0

    # Combine results
    result = {
        "followers": followers_count,
        "total_likes": total_likes,
        "total_views": total_views,
        "total_comments": total_comments,
        "avg_likes": avg_likes,
        "avg_views": avg_views,
        "avg_comments": avg_comments,
        "avg_engagement_rate": avg_engagement,
    }

    # Define the POST API endpoint
    post_url = "https://hook.eu2.make.com/6asghw6bevroa8fapd9devh4sobqd5p9"

    # Send the result to the POST API
    post_response = requests.post(post_url, json=result)

    if post_response.status_code == 200:
        print("Data successfully sent to the POST endpoint.")
    else:
        print(f"Failed to send data. HTTP Status Code: {post_response.status_code}")
        print(post_response.text)

else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
    print(response.text)





