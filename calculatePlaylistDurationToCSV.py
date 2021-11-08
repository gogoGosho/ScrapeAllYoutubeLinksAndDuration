import os, re, csv, isodate, datetime, pprint
from datetime import timedelta
from googleapiclient.discovery import build
import pandas as pd

os.chdir(r"")  # enter the direction(folder) of this python and headers.csv if you plan on making a bat file n shit
api_key = os.environ.get("YT_API_KEY")  # you have to create your own api key
youtube = build("youtube", "v3", developerKey=api_key)
hours_pattern = re.compile(r"(\d+)H")
minutes_pattern = re.compile(r"(\d+)M")
seconds_pattern = re.compile(r"(\d+)S")
total_seconds = 0
nextPageToken = None
while True:
    pl_request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=" ",  # enter the id of ur playlist, you can keep it(the playlist) hidden, just don't private it
        maxResults=50,
        pageToken=nextPageToken,
    )

    pl_response = pl_request.execute()
    vid_ids = []

    for item in pl_response["items"]:
        vid_ids.append(item["contentDetails"]["videoId"])
    vid_request = youtube.videos().list(part="contentDetails", id=",".join(vid_ids))

    vid_response = vid_request.execute()

    for item in vid_response["items"]:
        duration = item["contentDetails"]["duration"]
        hours = hours_pattern.search(duration)
        minutes = minutes_pattern.search(duration)
        seconds = seconds_pattern.search(duration)
        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0

        video_seconds = timedelta(
            hours=hours, minutes=minutes, seconds=seconds
        ).total_seconds()

        total_seconds += video_seconds
        nextPageToken = pl_response.get("nextPageToken")

    if not nextPageToken:
        break
total_seconds = int(total_seconds)
minutes, seconds = divmod(total_seconds, 60)
hours, minutes = divmod(minutes, 60)
print("Current duration in the playlist(privated videos or deleted videos excluded):")
print(f"{hours}h:{minutes}m:{seconds}s")


forKeepingVidIDS = vid_ids

forKeepingVidDUR = []
for item in vid_response["items"]:
    forKeepingVidDUR.append(item["contentDetails"]["duration"])

parsedDUR = []
for i in range(len(forKeepingVidDUR)):
    asd = int(isodate.parse_duration(forKeepingVidDUR[i]).total_seconds())
    parsedDUR.append(asd)
emmpy = dict(zip(forKeepingVidIDS, parsedDUR))
pformatedEmmpy = pprint.pformat(emmpy)

lines = open("headers.csv", "r").read()             #you can name this file whatever you want, just make sure that the first line in the file has VIDID,LENGHT    (under VIDID-the ids, under LENGHT-the lenght in seconds)
with open("headers.csv", "a+", newline="") as fp:   #this checks whether or not the file is already in the csv, if it is, it skips adding it, if not - it adds it
    writer = csv.writer(fp)
    for key, value in emmpy.items():
        if key in lines:
            continue
        else:
            writer.writerow([key, value])


# seconds to time
df = pd.read_csv("headers.csv")
totalaSeconds = int(df["LENGTH"].sum())
convertedTotal = datetime.timedelta(seconds=totalaSeconds)
print("Duration of the videos in the csv file: \n" + str(convertedTotal))
