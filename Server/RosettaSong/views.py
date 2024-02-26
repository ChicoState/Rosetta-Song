from django.shortcuts import redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy, load_backend
from social_core.actions import do_auth
from ytmusicapi import YTMusic

def google_login(request):
    """
    Initiates the Google OAuth login flow.
    """
    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
    return do_auth(backend)

@login_required
def ytauthentication(request):
    """
    Uses the authenticated user's Google OAuth token to interact with the YTMusic API.
    """
    try:
        social = request.user.social_auth.get(provider='google-oauth2')
        access_token = social.extra_data['access_token']
    except UserSocialAuth.DoesNotExist:
        return HttpResponse("User is not authenticated with Google.", status=401)
    ytmusic = YTMusic()
    ytmusic.setup(headers_raw=f'Authorization: Bearer {access_token}')

    # Example interaction with ytmusicapi
    try:
        liked_songs = ytmusic.get_liked_songs(limit=10)
        liked_song_titles = [song['title'] for song in liked_songs['tracks']]
    except Exception as e:
        return HttpResponse(f"Failed to access YouTube Music API: {str(e)}", status=500)

    return HttpResponse(f"User's Liked Songs: {', '.join(liked_song_titles)}", status=200)
