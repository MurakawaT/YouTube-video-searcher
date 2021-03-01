from django.core.management.base import BaseCommand

import requests
import json
from apiclient.discovery import build
import os
import time
import requests
import pandas as pd

from scapp.models import SearchData
from scapp.models import HoldChannel
from scapp.models import Channel
from scapp.models import Movie
from scapp.models import Comment

from apiclient.discovery import build

from .local_api_key import *

class Command(BaseCommand):
    def handle(self, *args, **options):

        print("---------scraping----------")
        holdChannels = HoldChannel.objects.order_by("created_date")

        for holdChannel in holdChannels:
            print()
            SEARCH_TEXT = holdChannel.search_word
            
            if holdChannel.status == 0:

                
                print("search channel =",SEARCH_TEXT)

                print("check search data")
                searchData = SearchData.objects.filter(search_word = SEARCH_TEXT)

                if searchData.exists():

                    print("exist searchData")
                    holdChannel.delete()
                    searchData[0].how_many += 1

                    continue

                channel_info = get_channel_info(SEARCH_TEXT)

                if len(channel_info) == 3:
                    channel_name, channel_yid, playlist_yid = channel_info

                    if len(Channel.objects.filter(channel_yid=channel_yid, status=1)) > 0:
                        print("すでに計算済みチャンネルがデータに存在")
                        searchData = SearchData(
                            search_word = SEARCH_TEXT,
                            status = 1,
                            channel_yid = holdChannel.channel_yid,
                            how_many = 1
                        )
                        searchData.save()
                        holdChannel.delete()

                        continue

                    holdChannel.status = 1
                    holdChannel.channel_yid = channel_yid
                    holdChannel.playList_yid = playlist_yid
                    holdChannel.channel_name = channel_name
                    holdChannel.save()
                    
                    channel = Channel(
                        channel_name=channel_name,
                        status = 0,
                        channel_yid = channel_yid,
                    )
                    channel.save()
                else:
                    holdChannel.delete()
                    searchData = SearchData(
                        search_word = SEARCH_TEXT,
                        status = 0,
                        how_many = 1
                    )
                    searchData.save()
                    continue

            channel = Channel.objects.filter(channel_yid=holdChannel.channel_yid)[0]

            if holdChannel.status == 1:
                print("get videos")

                response_playlist = get_video_info(
                    playList_yid = holdChannel.playList_yid,
                    pageToken = holdChannel.now_token
                )

                titles, urls, token = response_playlist

                for i, (title, url) in enumerate(zip(titles, urls)):
                    print("\r",((100*i)//len(titles)),"%", end="")
                    movie = Movie(
                        channel = channel,
                        movie_title=  title,
                        movie_url = url
                    )
                    movie.save()
                
                if token == "end":
                    print("complete getting videos")
                    holdChannel.status = 2
                    holdChannel.now_token = None
                else:
                    holdChannel.now_token = token
                    holdChannel.save()
                    exit()
                holdChannel.save()


            if holdChannel.status == 2:
                print("get comments per video")
                movies = Movie.objects.filter(channel=channel).order_by("id")
                count_moveis = 0
                for movie in movies:
                    count_moveis += 1
                    print("\r",((100*count_moveis)// len(movies)),"%", end="")
                    movie_yid = movie.movie_url.split("watch?v=")[-1]
                    if holdChannel.now_token and holdChannel.now_token != movie_yid:
                        continue

                    r_comments, holdChannel.now_token = get_comment_info(movie_yid)

                    holdChannel.status = 3
                    holdChannel.save()
                    
                    for r_comment in r_comments:
                        comment = Comment(
                            channel = channel,
                            movie = movie,
                            comment_text = r_comment
                        )
                        comment.save()
                if not holdChannel.now_token:
                    holdChannel.status = 3
                    holdChannel.save()
                
                    print("get comment")
                else:
                    exit()


def get_comment_info(video_yid):

    youtube = get_youtube_api()

    comments = []

    try:
        response_comments = youtube.commentThreads().list(
            part="snippet",
            maxResults=100,
            order="relevance",  # コメント関連度（?）順に整列
            videoId=video_yid
        ).execute()
    except:
        print("comments phase : max quota")
        return(comments, video_yid)
     # 失敗したとき今のvideo_IDを返す

    for response_comment in response_comments.get("items"):
        txt = response_comment["snippet"]['topLevelComment']['snippet']['textOriginal']
        comments.append(txt)

    return (comments, None)


def get_video_info(playList_yid, pageToken=None):
    
    youtube = get_youtube_api()

    movie_titles = []
    movie_urls = []

    while True:
        #--------------------------------
        # try break 入れるかも
        try:
            response_playlist = youtube.playlistItems().list(
                playlistId = playList_yid, 
                maxResults = 50, 
                pageToken = pageToken, 
                part = "snippet"
            ).execute()
        except:
            print("video phase : max quota")
            return(movie_titles, movie_urls, pageToken)
        
        # 失敗したときreturn(movie_titles, movie_urls, pageToken)
        this_page_result_num = len(response_playlist["items"])
        for i in range(0, this_page_result_num):
            movie_title = response_playlist["items"][i]["snippet"]["title"]
            movie_id = response_playlist["items"][i]["snippet"]["resourceId"]["videoId"]
            movie_url = "https://www.youtube.com/watch?v=" + movie_id

            movie_titles.append(movie_title)
            movie_urls.append(movie_url)
        
        print(pageToken)
        if not "nextPageToken" in response_playlist.keys():
            pageToken = "end"
            break
        else:
            pageToken = response_playlist["nextPageToken"]
    
    return (movie_titles, movie_urls, pageToken)


def get_channel_info(SEARCH_TEXT):

    youtube = get_youtube_api()

    #----------channel.list()----------------------
    print("use youtube data api --channel.list()")
    # username　から　チャンネルID
    try:
        part = "id,snippet,contentDetails,statistics"
        response_channel = youtube.channels().list(
            forUsername=SEARCH_TEXT,
            part=part, 
            maxResults=1
        ).execute()
    except:
        print("max quota")
        exit()
        # 失敗したとき
    if "items" in response_channel.keys():
        playlist_yid = response_channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        channel_yid =  response_channel["items"][0]["id"]
        channel_name = response_channel["items"][0]["snippet"]["title"]
        video_count = response_channel["items"][0]["statistics"]["videoCount"]
        print(channel_yid)
        print(channel_name)
        print(playlist_yid)
        print(video_count)
        print("get channel info from channel.list()!!")
        return (channel_name, channel_yid, playlist_yid)


    #----------search.list()-----------------------
    print("use youtube data api --serach.list()")
    # 検索ワードから直接サーチ
    try:
        part = "snippet"
        response_search = youtube.search().list(
            part = part, 
            maxResults = 5, 
            q = SEARCH_TEXT
        ).execute()
    except:
        print("maxquota")
        exit()
        # 失敗したとき
    for item in response_search["items"]:
        if item["id"]["kind"] == "youtube#channel":
            try:
                channel_yid = item["snippet"]["channelId"]
                part = "id,snippet,contentDetails,statistics"
                response_channel = youtube.channels().list(
                    id=channel_yid,
                    part=part, 
                    maxResults=1
                ).execute()
            except:
                print("maxquota")
                exit()
            # 失敗したとき
            playlist_yid = response_channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            channel_yid =  response_channel["items"][0]["id"]
            channel_name = response_channel["items"][0]["snippet"]["title"]
            video_count = response_channel["items"][0]["statistics"]["videoCount"]
            print(channel_yid)
            print(channel_name)
            print(playlist_yid)
            print(video_count)
            print("get channel info from search.list()!!")
            return (channel_name, channel_yid, playlist_yid)

    print( "NO DATA in YouTube")
    return ("nodata")

def get_youtube_api():
    #--------------------------------
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=API_KEY
    )
    return youtube

