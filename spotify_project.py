import requests
import pandas as pd
import os


client_id = '24952d94fa244494a1b84f6197f1b9a0'
client_secret = 'bb9eea6bffed41689c94502a93a7c4c6'

auth_response = requests.post(
    'https://accounts.spotify.com/api/token',
    data={'grant_type': 'client_credentials'},
    auth=(client_id, client_secret)
)

if auth_response.status_code != 200:
    print("❌ Failed to authenticate.")
    print(auth_response.json())
    exit()

access_token = auth_response.json()['access_token']
headers = {'Authorization': f'Bearer {access_token}'}


while True:
    try:
        num_artists = int(input("🎤 How many artists do you want to enter? (1 to 5): "))
        if 1 <= num_artists <= 5:
            break
        else:
            print("⚠️ Please enter a number between 1 and 5.")
    except ValueError:
        print("⚠️ Please enter a valid number.")


artist_inputs = []
for i in range(num_artists):
    artist_name = input(f"📝 Enter artist #{i+1} name: ").strip()
    artist_inputs.append(artist_name)

artist_summaries = []
all_tracks = []


for artist_name in artist_inputs:
    
    search_resp = requests.get(
        'https://api.spotify.com/v1/search',
        headers=headers,
        params={'q': artist_name, 'type': 'artist', 'limit': 1}
    )

    items = search_resp.json().get('artists', {}).get('items', [])
    if not items:
        print(f"❌ No artist found for: {artist_name}")
        continue

    artist = items[0]
    artist_id = artist['id']
    artist_real_name = artist['name']
    artist_popularity = artist['popularity']
    artist_followers = artist['followers']['total']

    print(f"\n🎶 Found Artist: {artist_real_name}")
    print(f"   - Followers: {artist_followers:,}")
    print(f"   - Popularity Score: {artist_popularity}/100")

   
    artist_summaries.append({
        'name': artist_real_name,
        'followers': artist_followers,
        'popularity': artist_popularity
    })

   
    top_tracks_resp = requests.get(
        f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks',
        headers=headers,
        params={'market': 'US'}
    )

    top_tracks = top_tracks_resp.json().get('tracks', [])
    for t in top_tracks:
        all_tracks.append({
            'artist': artist_real_name,
            'track_name': t['name'],
            'album': t['album']['name'],
            'release_date': t['album']['release_date'],
            'duration_ms': t['duration_ms'],
            'popularity': t['popularity'],
            'explicit': t['explicit'],
            'preview_url': t['preview_url'],
            'spotify_url': t['external_urls']['spotify']
        })


if artist_summaries:
    most_popular = max(artist_summaries, key=lambda x: x['popularity'])
    print(f"\n🏆 Most popular artist: {most_popular['name']} with a popularity score of {most_popular['popularity']}/100")


df = pd.DataFrame(all_tracks)

if not df.empty:
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'spotify_top_tracks_all_artists.csv')
    df.to_csv(downloads_path, index=False)
    print(f"\n✅ CSV saved: {downloads_path}")
else:
    print("⚠️ No tracks were saved.")
