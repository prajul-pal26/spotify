from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
import requests      # this check if any user loggin to the page or not 
import base64
import requests
import json
#--------------------------------------------------get token -> get autorization header-------------------------
def get_token():
    client_id = '59a919435d414df88f288b5a7bcc45c6'
    client_secret = '100bd40eed1143399e55a3ed9d639c00'

    # Encode client ID and client secret in base64
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    # Spotify token endpoint URL
    token_url = 'https://accounts.spotify.com/api/token'

    # Data for the POST request
    token_data = {
        'grant_type': 'client_credentials'
    }

    # Headers for the POST request
    token_headers = {
        'Authorization': f'Basic {client_creds_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the POST request to get the token
    response = requests.post(token_url, data=token_data, headers=token_headers)

    # Check if the request was successful
    if response.status_code == 200:
        token_response_data = response.json()
        access_token = token_response_data['access_token']
        return access_token

def get_auth_header(token):
    return {"Authorization":"Bearer "+token}
def convert_milliseconds(milliseconds):
    seconds = (milliseconds // 1000) % 60
    minutes = (milliseconds // (1000 * 60)) % 60
    
    return f"{minutes}:{seconds:02d}"
#-----------------------------------------------------search by track------------------------------
def search(request):
    if request.method=="POST":
        search_query=request.POST['search_query']
        #----------------same search as top artist
        url=f"https://api.spotify.com/v1/search?q={search_query}&type=artist&limit=1"
        headers = get_auth_header(get_token())
        
        response = requests.get(url, headers=headers)
        data=response.json()
        id=data["artists"]['items'][0]['id'] 
        #----------------top songs by artist
        songs_url=f"https://api.spotify.com/v1/artists/{id}/top-tracks?market=IN"
        headers2 = get_auth_header(get_token())
        
        response = requests.get(songs_url, headers=headers2)
        data2=response.json()
        
    
        search_results_count=len(data2['tracks'])
        tracks=data2['tracks']
        track_list=[]
        for track in tracks:
            track_name=track['name']
            artist_name=track['artists'][0]['name']
            duration=track['duration_ms']
            trackid=track['id']
            track_image=track['album']['images'][0]['url']
            track_list.append({
                'track_name':track_name,
                'artist_name':artist_name,
                'duration':convert_milliseconds(int(duration)),
                'trackid':trackid,
                'track_image':track_image
            })
        context={
            'search_results_count':search_results_count,
            'track_list': track_list,
        }
    return render(request,'search.html',context)

#-----------------------------------------------top artist -> their profile  --------------------------------------------
def profile(request,pk):
    url=f"https://api.spotify.com/v1/artists/{pk}"
    headers = get_auth_header(get_token())
    
    response = requests.get(url, headers=headers)

    data=response.json()
    name =data['name']
    monthly_listener=data['followers']['total']
    artist_url=data['images'][0]['url']
    artist_data={
        'name':name,
        'monthlyListeners':monthly_listener,
        'headerUrl':artist_url
    }
    
    return render(request,'profile.html',artist_data)
#artist id
def top_artists():
    list_of_artist=["Arijit Singh","Shreya Ghoshal","Armaan Malik","Neha Kakkar","A. R. Rahman","Jubin Nautiyal"]
    details=[]
    for artist in list_of_artist:
        url=f"https://api.spotify.com/v1/search?q={artist}&type=artist&limit=1"
        headers=get_auth_header(get_token())   
        result=requests.get(url,headers=headers)
        data=json.loads(result.content)
        
        image=data["artists"]['items'][0]['images'][0]['url']
        name=data["artists"]['items'][0]['name']
        id=data["artists"]['items'][0]['id']      
        details.append((name,image,id))
    return details
#---------------------------------------top song -> music play---------------------------------------

def music(request,pk):
    track_id = pk

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    headers=get_auth_header(get_token())

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        track_name = data['album']['name']
        first_artist_name = data['album']['artists'][0]['name']
        track_image = data['album']['images'][1]['url']
        
        audio_url=data['preview_url']
        duration_text=convert_milliseconds(int(data['duration_ms']))
        
        context = {
            'track_name': track_name,
            'artist_name': first_artist_name,
            'audio_url': audio_url,
            'duration_text': duration_text,
            'track_image': track_image,
        }
        return render(request, 'music.html', context)
#song _id
def top_songs():
    #top songs by category
    url=f"https://api.spotify.com/v1/playlists/37i9dQZF1DXdpQPPZq3F7n/tracks?limit=15"

    headers=get_auth_header(get_token())
    result=requests.get(url,headers=headers)
    json_result=json.loads(result.content)
    shortened_data=json_result['items']

    track_details=[]
    for track in shortened_data:
        track_id = track['track']['id']
        track_name = track['track']['album']['name']
        cover_url = track['track']['album']['images'][0]['url']

        track_details.append({
            'id': track_id,
            'name': track_name,
            'cover_url': cover_url
        })
    return track_details
#------------------------------------------------------------------------------------------------------------
@login_required(login_url='login')
def index(request):
    artists_info = top_artists()
    top_track_list = top_songs()

    # divide the list into three parts
    first_six_tracks = top_track_list[:5]
    second_six_tracks = top_track_list[5:10]
    third_six_tracks = top_track_list[10:15]

    context = {
        'artists_info' : artists_info,
        'first_six_tracks': first_six_tracks,
        'second_six_tracks': second_six_tracks,
        'third_six_tracks': third_six_tracks,
    }

    return render(request, 'index.html', context)
def login(request):
    if request.method == "POST":
        username=request.POST['username']  
        password=request.POST['password']  
        user=auth.authenticate(username=username,password=password)
        
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else: 
            messages.info(request,'Credentials Invalid')
            return redirect('login')        
        
    return render(request, "login.html")
def signup(request):
    if request.method == "POST":
        email=request.POST['email']         # email is the name which we define in the html page in the html 
        username=request.POST['username']  
        password=request.POST['password']  
        password2=request.POST['password2'] 
        
        if password==password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,"Email Taken")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,"username Taken")
                return redirect('signup')
            else:
                user=User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # now login to the user to the same page 
                user_login=auth.authenticate(username=username, password=password)
                auth.login(request,user_login)
                return redirect("/")
        else:
            messages.info(request,'Password Not Matching')
            return redirect('signup') 
    else:
        return render(request, "signup.html")
@login_required(login_url='login')
def logout(request):
    # auth.logout(request)
    return redirect('login')
    
    