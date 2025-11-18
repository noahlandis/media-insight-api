import random 

async def get_channel_overview(google_client, google_session):
    """
    Returns publishedAt, channel name, description
    """
    resp = await google_client.get('youtube/v3/channels', params={'mine': True, 'part': 'snippet'}, token=google_session)
    data = resp.json()
    return data

async def get_channel_stats(google_client, google_session):
    """
    Returns viewCount, subscriberCount, videoCount. Note that viewCount here only counts videos listed as public. (includes both long for and shorts)
    """
    resp = await google_client.get('youtube/v3/channels', params={'mine': True, 'part': 'statistics'}, token=google_session)
    data = resp.json()
    return data

async def _get_upload_playlist_id(google_client, google_session):
    """
    helper function to get the playlist id so uploaded videos can be retrieved
    """
    resp = await google_client.get('youtube/v3/channels', params={'mine': True, 'part': 'contentDetails'}, token=google_session)
    data = resp.json()
    upload_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print(upload_playlist_id)
    return upload_playlist_id


async def get_videos(google_client, google_session):
    """
    Returns list of videos. Each video includes title, description, publishedAt, videoId
    """
    upload_playlist_id = await _get_upload_playlist_id(google_client, google_session)
    videos = {}
    next_page_token = None
    while True:
        resp = await google_client.get('youtube/v3/playlistItems', params={'mine': True, 'part': 'snippet', 'playlistId': upload_playlist_id, 'pageToken': next_page_token, 'maxResults': 50}, token=google_session)
        data = resp.json()
        for item in data['items']:
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']

            videos[video_id] = {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'publishedAt': snippet['publishedAt']
            }

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break



    # print("Number of videos")
    # print(len(videos))
    # print()
    # print("Results")
    # for key, value in videos.items():
    #     print(f"{key}: {value}")
    #     print()
    return videos

async def get_video_count_playlist_api(google_client, google_session):
    """
    Returns the number of videos 'totalResults' (for both longform and shorts), regardless of visibility settings (uses part: id to ensure the smallest response, in case the user is only interested in the total number of videos)
    """
    upload_playlist_id = await _get_upload_playlist_id(google_client, google_session)
    resp = await google_client.get('youtube/v3/playlistItems', params={'mine': True, 'part': 'id', 'playlistId': upload_playlist_id, 'maxResults': 0}, token=google_session)
    data = resp.json()
    print(data['pageInfo']['totalResults'])


async def get_video_details(google_client, google_session, videos, parts=None):
    """
    Returns list of videos including duration, definition, caption (boolean so True/False), viewCount, likeCount, dislikeCount, favoriteCount, commentCount, and privacyStatus (public, private, unlisted)
    """
    if parts is None:
        parts = ['contentDetails', 'statistics', 'status']
    for i, batch in enumerate(range(0, len(videos), 50)):
        batch_ids = list(videos.keys())[batch:batch+50]
        resp = await google_client.get(
            'youtube/v3/videos',
            params={
                'part': ','.join(parts),
                'id': ','.join(batch_ids)
            },
            token=google_session
        )
        data = resp.json()

        for item in data.get('items', []):
            vid = item['id']
            if vid not in videos:
                continue

            # 1) contentDetails
            if 'contentDetails' in parts:
                details = item.get('contentDetails', {})
                videos[vid].update({
                    'duration': details.get('duration'),
                    'definition': details.get('definition'),
                    'caption': details.get('caption'),
                })

            # 2) statistics
            if 'statistics' in parts:
                stats = item.get('statistics', {})
                videos[vid].update({
                    'viewCount': stats.get('viewCount'),
                    'likeCount': stats.get('likeCount'),
                    'dislikeCount': stats.get('dislikeCount'),  # often not present
                    'favoriteCount': stats.get('favoriteCount'),
                    'commentCount': stats.get('commentCount'),
                })

            # 3) status
            if 'status' in parts:
                status = item.get('status', {})
                videos[vid].update({
                    'privacyStatus': status.get('privacyStatus'),
                })
    # print("Number of videos")
    # print(len(videos))
    # print()
    # print("Results")
    # for key, value in videos.items():
    #     print(f"{key}: {value}")
    #     print()

    print_videos(videos)
    return videos


async def get_video_content_details(google_client, google_session):
    """
    Return's the video's duration, caption, definition
    """
    resp = await google_client.get('youtube/v3/videos', params={'part': 'contentDetails', 'id': video_ids[0]}, token=google_session)
    data = resp.json()


async def get_video_statistics(google_client, google_session):
    """
    Return's the video's viewCount, likeCount, dislikeCount, favoriteCount, commentCount
    """
    resp = await google_client.get('youtube/v3/videos', params={'part': 'statistics', 'id': video_ids[0]}, token=google_session)
    data = resp.json()

async def get_video_privacy_status(google_client, google_session):
    """
    Return's the video's privacy status
    """
    resp = await google_client.get('youtube/v3/videos', params={'part': 'status', 'id': video_ids[0]}, token=google_session)
    data = resp.json()

async def get_public_videos(google_client, google_session):
    """
    Retrieve video details and return only public videos.
    """
    videos = await get_video_details(google_client, google_session)

    # Filter the dictionary for videos whose privacyStatus is 'public'
    public_videos = {
        vid: details
        for vid, details in videos.items()
        if details.get("privacyStatus") == "public"
    }

    print_videos(public_videos)

    return public_videos


async def get_channel_overview_analytics(google_client, google_session):
    """
    gets views (both public, private, unlisted), comments, likes, dislikes, estimatedMinutesWatched, averageViewDuration, subscribersGained, subscribersLost
    """
    resp = await google_client.get(
        'https://youtubeanalytics.googleapis.com/v2/reports',
        params={
            'ids': 'channel==MINE',
            'startDate': '2005-10-01',
            'endDate': '2025-11-11',
            "metrics": "views,comments,likes,dislikes,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost",
        },
        token=google_session
    )

    data = resp.json()

    # method 1
    if not data.get("rows"):
        return {}

    headers = [h["name"] for h in data["columnHeaders"]]
    row = data["rows"][0]
    table = dict(zip(headers, row))
    return table

    # # method 2
    # view_index = next(
    #     i for i, col in enumerate(data["columnHeaders"])
    #     if col["name"] == "views"
    # )
    # views = data["rows"][0][view_index]
    



    # return table

    t = [col for col in enumerate(data["columnHeaders"])]
    print(t)
    return data


async def get_top_viewed_video_ids_analytics(google_client, google_session):
    """
    gets videos ids (both public, private, unlisted), and each of their views comments, likes, dislikes, estimatedMinutesWatched, averageViewDuration, subscribersGained, subscribersLost, shares. Sorts by views
    """
    resp = await google_client.get(
        'https://youtubeanalytics.googleapis.com/v2/reports',
        params={
            'ids': 'channel==MINE',
            'startDate': '2005-10-01',
            'endDate': '2025-11-10',   # same as your other call
            'metrics': (
                'views,comments,likes,dislikes,'
                'estimatedMinutesWatched,averageViewDuration,'
                'subscribersGained,subscribersLost'
            ),
            'dimensions': 'video',
            'sort': '-views',          # REQUIRED for this report type
            'maxResults': 200,    
        },
        token=google_session
    )
    data = resp.json()
    print(data)



async def get_video_count_search_api(google_client, google_session):
    """
    Returns the number of videos 'totalResults' (for both longform and shorts), regardless of visibility settings (doesn't require upload playlist id)
    """
    resp = await google_client.get(
        'youtube/v3/search',
        params={
            'part': 'snippet',
            'forMine': True,
            'type': 'video',
            'maxResults': 0
        },
        token=google_session
    )
    data = resp.json()
    print(data['pageInfo']['totalResults'])
        
        

async def get_public_videos_search_api(google_client, google_session):
    """
    gets public videos. Defaults to sorting by relevancy (doesn't require upload playlist id). Note: channel id is required and it will only return public videos
    """
    resp = await google_client.get('youtube/v3/channels', params={'mine': True}, token=google_session)
    data = resp.json()
    channel_id = data['items'][0]['id']
    videos = {}
    next_page_token = None
    while True:
        resp = await google_client.get(
            'youtube/v3/search',
            params={
                'part': 'snippet',
                'channelId': channel_id,
                'type': 'video',
                'maxResults': 50,
                'pageToken': next_page_token
            },
            token=google_session
        )
        data = resp.json()
  
        for item in data['items']:
            snippet = item['snippet']
            video_id = item['id']['videoId']

            videos[video_id] = {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'publishedAt': snippet['publishedAt']
            }


        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    
    print("Regular API called with channel id. No sort")
    print_videos(videos)
    return videos

async def get_public_videos_search_api_sort(google_client, google_session, sort, channel_id):
    """
    gets public videos and sort by date, rating, relevence, title, viewCount. (doesn't require upload playlist id). Note: channel id is required and it will only return public videos. Still call sort if sorting by viewCount because of known issue
    """
    videos = {}
    next_page_token = None
    while True:
        resp = await google_client.get(
            'youtube/v3/search',
            params={
                'part': 'snippet',
                'channelId': channel_id,
                'type': 'video',
                'order': sort,
                'maxResults': 50,
                'pageToken': next_page_token
            },
            token=google_session
        )
        data = resp.json()
  
        for item in data['items']:
            snippet = item['snippet']
            video_id = item['id']['videoId']

            videos[video_id] = {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'publishedAt': snippet['publishedAt']
            }


        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    
    print("------------------------------------------------------")
    print("Regular API called with channel id. Sorting by: ", sort)
    print_videos(videos)
    print("-----------------------------------------------------")
    return videos

async def get_public_videos_sort_test(google_client, google_session):
    resp = await google_client.get('youtube/v3/channels', params={'mine': True}, token=google_session)
    data = resp.json()
    channel_id = data['items'][0]['id']
    print()
    await get_public_videos_search_api_sort(google_client, google_session, 'date', channel_id)
    await get_public_videos_search_api_sort(google_client, google_session, 'rating', channel_id)
    await get_public_videos_search_api_sort(google_client, google_session, 'relevance', channel_id)
    await get_public_videos_search_api_sort(google_client, google_session, 'title', channel_id)
    await get_public_videos_search_api_sort(google_client, google_session, 'viewCount', channel_id)






async def get_all_videos_search_api(google_client, google_session):
    """
    gets video ids, title, description, published at (doesn't require upload playlist id). Should be called if user wants all videos (regardless of visibility). Default sorts to publishedAt
    """
    videos = {}
    next_page_token = None
    while True:
        resp = await google_client.get(
            'youtube/v3/search',
            params={
                'part': 'snippet',
                'forMine': True,
                'type': 'video',
                'maxResults': 50,
                'pageToken': next_page_token
            },
            token=google_session
        )
        data = resp.json()
        for item in data['items']:
            snippet = item['snippet']
            video_id = item['id']['videoId']

            videos[video_id] = {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'publishedAt': snippet['publishedAt']
            }

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break



    print("Showing videos with no search query included")
    print_videos(videos)

    return videos


async def get_all_videos_rough_sort_by_views(google_client, google_session):
    """
    Gets video ids regardless of scope and ROUGHLY sorts them by viewCount because of API quirk. Also includes title, description, published at. 
    This function can be used only in a case where a user wants to sort all videos (regardless of visibility) by viewCount. The /videos API must still collect the views, and
    a manual sort should still be called to correct the out of place sorts.
    """
    videos = {}
    next_page_token = None
    while True:
        resp = await google_client.get(
            'youtube/v3/search',
            params={
                'part': 'snippet',
                'forMine': True,
                'type': 'video',
                'order': 'viewCount',
                'maxResults': 50,
                'pageToken': next_page_token
            },
            token=google_session
        )
        data = resp.json()
        for item in data['items']:
            snippet = item['snippet']
            video_id = item['id']['videoId']

            videos[video_id] = {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'publishedAt': snippet['publishedAt']
            }

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break



    return videos


def print_videos(videos):
    print("-------------------------------------------------------------------------")
    print("Number of videos:")
    print(len(videos))
    print()
    print("Results:")
    for key, value in videos.items():
        print(f"{key}: {value}")
        print()
    print("-------------------------------------------------------------------------")



"""
Test filters for /search including videoDuration, videoDefinition, videoCaption, q, publishedBefore, publishedAfter
"""