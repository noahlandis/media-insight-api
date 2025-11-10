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
    videos = []
    next_page_token = None
    while True:
        resp = await google_client.get('youtube/v3/playlistItems', params={'mine': True, 'part': 'snippet', 'playlistId': upload_playlist_id, 'pageToken': next_page_token, 'maxResults': 50}, token=google_session)
        data = resp.json()
        for item in data['items']:
            snippet = item['snippet']
            videos.append({
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'publishedAt': snippet['publishedAt'],
                'videoId': snippet['resourceId']['videoId'],
        })
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break



    print(videos)