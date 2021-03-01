from django.urls import path
from scapp import views

app_name = 'scapp'
urlpatterns = [
    path('top/', views.scapp_top, name='scapp_top'),   # トップ画面
    path('topic_search/', views.scapp_search, name='scapp_search'),  # トピックリスト or チャンネル一覧
    path('topic_list/<int:channel_id>/<int:maxtopic_num>/', views.scapp_list, name='scapp_list'),
    path('detail/<int:topicImage_id>/', views.scapp_detail, name='scapp_detail'),  # 詳細
]