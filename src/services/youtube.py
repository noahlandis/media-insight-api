import random 

async def get_channel_overview(google_client, google_session):
    """
    Returns publishedAt, channel name, description
    """
    resp = await google_client.get('youtube/v3/channels', params={'mine': True, 'part': 'snippet'}, token=google_session)
    data = resp.json()
    print(data)

async def get_channel_stats(google_client, google_session):
    """
    Returns viewCount, subscriberCount, videoCount. Note that viewCount here only counts videos listed as public. (includes both long for and shorts)
    """
    resp = await google_client.get('youtube/v3/channels', params={'mine': True, 'part': 'statistics'}, token=google_session)
    data = resp.json()
    print(data)

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



    # print(videos)
    return videos

async def get_video_count(google_client, google_session):
    """
    Returns the number of videos 'totalResults' (for both longform and shorts), regardless of visibility settings (uses part: id to ensure the smallest response, in case the user is only interested in the total number of videos)
    """
    upload_playlist_id = await _get_upload_playlist_id(google_client, google_session)
    resp = await google_client.get('youtube/v3/playlistItems', params={'mine': True, 'part': 'id', 'playlistId': upload_playlist_id}, token=google_session)
    data = resp.json()
    print(data['pageInfo']['totalResults'])


async def get_video_details(google_client, google_session, parts=None):
    """
    
    """
    if parts is None:
        parts = ['contentDetails', 'statistics', 'status']
    videos = await get_videos(google_client, google_session)
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
    random_key = random.choice(list(videos.keys()))
    print(random_key, videos[random_key])
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

