import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyD-dSxr8fi2N58WtXi5c7bBYIgHZFODtwc"

# YouTube API URLs
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Field
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of Self-Development Keywords
keywords = [
    "Self Improvement", "Self Development", "Personal Growth", "Personal Development",
    "Self Help", "Growth Mindset", "Productivity", "Success Habits", "Discipline",
    "Motivation", "Morning Routine", "Life Advice", "Mindset Shift",
    "Change Your Life", "Better Version of Yourself", "Time Management",
    "Self Discipline", "Mind Reprogramming", "Focus and Consistency",
    "Life Transformation"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Loop through keywords
        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            # Search API parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "videoDuration": "medium",  # Filter for videos 4–20 minutes
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            # Make search API call
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Skip if no results
            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Get video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            # Get channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            # Check for stats and channel data
            if "items" not in stats_data or "items" not in channel_data:
                st.warning(f"Failed to fetch stats for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Collect relevant results
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                # Filter: Only include channels under 3,000 subs
                if subs < 3000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Show results
        if all_results:
            st.success(f"Found {len(all_results)} videos from channels with under 3,000 subs!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("No matching videos found from small channels.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
