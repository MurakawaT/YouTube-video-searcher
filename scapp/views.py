from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from scapp.models import Channel, Movie, Comment, TopicImage, Ranking, SearchData, HoldChannel
from django.db.models import F
from django.urls import reverse


#viewsでずっと使う
maxtopic_range = [2,4,8,16,32]

# Create your views here.

def scapp_top(request):
    return render(request, "scapp/top.html",
        dict(
            maxtopic_range=maxtopic_range,
            maxtopic_num=4,
            )
        )
    # return HttpResponse("top画面")


def scapp_list(request, channel_id, maxtopic_num):
    # 作ったトピックイメージを取り出す
    channel = Channel.objects.filter(id=channel_id)[0]
    topic_images = TopicImage.objects.filter(channel=channel,  maxtopic_num=maxtopic_num).order_by('id')
    #listページの基礎情報項目の表示用
    movies = Movie.objects.filter(channel=channel)
    comments = Comment.objects.filter(channel=channel)
    return render(request, "scapp/topic_list.html", 
        dict(
            maxtopic_range=maxtopic_range,
            maxtopic_num=maxtopic_num,
            channel=channel,
            movies=movies,
            comments=comments,
            topic_images=topic_images,
        )
    )

def scapp_search(request):
    #Requestの読み込み

    notice_txt = ""
    maxtopic_num = 4

    if len(request.POST.keys()) != 0:
        search_text = request.POST["target_channel_name"]
        maxtopic_num = int(request.POST["maxtopic_num"])
        # print(request.POST)

        if search_text != "":
            # Search data から データベースに存在を確認
            searchData = SearchData.objects.filter(search_word=search_text)
            if len(searchData) > 0:
                # search 済み
                if searchData[0].status == 1:
                    # チャンネルが存在し計算も終了している
                    channel_yid = searchData[0].channel_yid
                    channel = Channel.objects.filter(channel_yid=channel_yid)[0]

                    return redirect('scapp:scapp_list', channel.id, maxtopic_num)

                else:
                    # そもそもチャンネルがネットに存在しない
                    notice_txt = "チャンネル「{}」は存在しません".format(search_text)
            else:
                if len(HoldChannel.objects.filter(search_word=search_text)) == 0:
                    #　seachDataにない。かつ HoldChannelに存在しない。
                    #　待機中 or スクレイピング中 or まだ検索されたことがない
                    notice_txt = "チャンネル「{}」は「解析待ち・解析中のチャンネル」に追加されました".format(search_text)
                    holdChannel = HoldChannel(
                        search_word = search_text,
                        status = 0,
                    )
                    holdChannel.save()
                else:
                    # seachDataにはないが HoldChannelに存在する。
                    notice_txt = "チャンネル「{}」は解析待ち、もしくは解析中です".format(search_text)

    # print(notice_txt)

    
    channels = Channel.objects.filter(status=1).order_by("channel_name")
    holdChannels = HoldChannel.objects.filter(status__lte=3).order_by("created_date")

    return render(request, "scapp/table.html", 
        dict(
            maxtopic_range=maxtopic_range,
            maxtopic_num=maxtopic_num,
            notice_txt = notice_txt,
            channels = channels,
            holdChannels = holdChannels,
        )
    )

def scapp_detail(request, topicImage_id):
    topicImage = get_object_or_404(TopicImage, pk=topicImage_id)  # topicImage取得
    maxtopic_num = topicImage.maxtopic_num
    channel = topicImage.channel
    rankings = Ranking.objects.filter(topicImage=topicImage).order_by("similarity").reverse()
    rankings = rankings[:min(50,len(rankings))]
    print(maxtopic_num, channel)

    return render(request, "scapp/detail.html", 
        dict(
            maxtopic_range=maxtopic_range,
            maxtopic_num=maxtopic_num,
            channel=channel,
            rankings=rankings,
            topic=topicImage,
        )
    )
    # return HttpResponse('動画一覧')