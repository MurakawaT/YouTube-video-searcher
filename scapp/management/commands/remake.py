from django.core.management.base import BaseCommand
from django.utils import timezone

import requests
import json
from apiclient.discovery import build
import os
import time
import requests
import pandas as pd
import time

from scapp.models import SearchData
from scapp.models import HoldChannel
from scapp.models import Channel
from scapp.models import Movie
from scapp.models import Comment


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("remake test")

        words = [
            "YUI OGURA おぐらゆい ASMR/Beauty", # cost 1 + 100 + 1
            "cod金太郎", # cost 1 + 100 + 1
            "NoCopyrightSounds", #cost 1 + 
        ]
        for i, word in enumerate(words):
            time.sleep(1.1)
            print(i, word)
            holdChannel = HoldChannel.objects.filter(search_word=word)
            if len(holdChannel) != 0:
                print("delete")
                holdChannel[0].delete()
            holdChannel = HoldChannel(
                search_word = word,
                status = 0,
            )
            holdChannel.save()
        