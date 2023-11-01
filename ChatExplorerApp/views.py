from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from ChatExplorerApp.Models.chatmodel import ChatModel
import json
from ChatExplorerApp.Models.commentmodel import CommentModel
from ChatExplorerApp.Models.usermodel import UserModel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.db.models import Max
from django.db.models import Q
from ChatExplorerApp.serializers import ChatModelSerializer, CommentModelSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


# Create your views here.


def index(request):
    
    return render(request,"index.html",{'show_login_card': True})


def save_to_db(request):
    #actual path of your CSV file
    file_path = './Files/ChatExport.json'
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        # Loop through JSON data and save to the database
        for item in json_data:
            chat_instance = ChatModel(
                sessionId=item['sessionId'],
                userId=item['userId'],
                messageId=item['messageId'],
                message=item['message'],
                createdAt=item['createdAt'],
                updatedAt=item['updatedAt'],
            )
            chat_instance.save()


        user_json_file = './Files/Users.json'
        with open(user_json_file, 'r') as file:
            data = json.load(file)  # Use json.load to load the JSON data

            for item in data:
                user = UserModel(
                    userId=item['userId'],
                    orgId=item['orgId'],
                    email=item['email'],
                    firstName=item['firstName'],
                    lastName=item['lastName'],
                    createdAt=item['createdAt'],
                    updatedAt=item['updatedAt'],
                    metadata=item['metadata']
                )
                user.save()
    except FileNotFoundError:
        print(f'File not found')
    except json.JSONDecodeError:
        print(f'Invalid JSON format in the file')
        

    return HttpResponse("Data saved to the database.")

# create new account
def signup(request):
    user_exist_check = False 
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        print(username,email,password)
        try:
            # Check if the user already exists
            user = User.objects.get(username=username)
            if user:
                print("User already exists.")
                user_exist_check = True  # Set the flag to True
                return render(request, "index.html", {'user_exist': user_exist_check,'show_signup_card': True})
            else:
                # Create a new user
                user = User.objects.create_user(username, email, password)                
                # Optionally, you can log in the user after signup
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    print("User created and logged in.")
                    # Redirect to a chat page 
                    return redirect('ChatExplorerApp:chat')

        except Exception as e:
            print(f"Database error: {e}")
            # Handle the error, e.g., display an error message to the user
            return render(request, "index.html", {'error_message': 'An error occurred during signup.','show_signup_card': True})

    return render(request, "signup.html",{'show_signup_card': True})  # Replace "signup.html" with your actual signup page template


# login
# Api Method for Getting All Session Data
def Userlogin(request):
    invalid_login = False
    loadercheck=True 
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)
            print("User logged in.")
            # Redirect to a chat page
            return redirect('ChatExplorerApp:chat')
        else:
            # Handle invalid login credentials
            print("Invalid login credentials.")
            invalid_login = True  # Set the flag to True
            return render(request,"index.html",{'invalid_login': invalid_login,'loadercheck': loadercheck,'show_login_card': True})

    return render(request,"signup.html")


# Api Method for Getting All Session Data
@api_view(['GET'])
def getsessions(request,user_id):
    session_list = ChatModel.objects.filter(userId=user_id).values('sessionId').annotate(latest_created=Max('createdAt'))
    sessions_data = [{'sessionId': session['sessionId'], 'latest_created': session['latest_created']} for session in session_list]
    return JsonResponse(sessions_data, safe=False)


# Method for render index view only if logged in
@login_required(login_url='/')
def chat(request):
    user_list = UserModel.objects.all()
    return render(request,'chat.html',{'user_list':user_list})

# Api Method for getting chat results with session_id and user_id
@api_view(['GET'])
def getchatresults(request,user_id,session_id):
    chat_result = ChatModel.objects.filter(Q(userId=user_id) | Q(userId="taiwa-bot"), sessionId=session_id)
    chat_serializer = ChatModelSerializer(chat_result,many=True)
    comment_result = CommentModel.objects.filter(Q(user_id=user_id) | Q(user_id="taiwa-bot"), session_id=session_id)
    comment_serializer = CommentModelSerializer(comment_result,many=True)
    response_data = {
        'chat_data': chat_serializer.data,
        'comment_data': comment_serializer.data,
    }
    print(response_data)
    return Response(response_data)


@api_view(['POST'])
def save_comment(request):
    if request.method == 'POST':
        try:
            comment = request.data['comment']
            session_id = request.data['session_id']
            user_id = request.data['user_id']
            # get id of logged user
            if request.user.is_authenticated:
                # Check if the user object has an 'id' attribute
                if hasattr(request.user, 'id'):
                    commented_user_id = request.user.id
                    # save comment to CommentModel
                    comment_data = CommentModel.objects.create(comment=comment, session_id=session_id, user_id=user_id,commented_user_id=commented_user_id)
                    
                    return JsonResponse({'status': 'success'})
                else:
                    raise AttributeError("User object does not have 'id' attribute")
        
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error saving comment: {e}")

            # Return an error response
            return JsonResponse({'status': 'error', 'message': 'Error saving comment'})
    else:
        # Return a bad request response if the request method is not POST
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# Api Method for getting comments with session_id and user_id
@api_view(['GET'])
def getcomments(request,user_id,session_id):
    comment_result = CommentModel.objects.filter(Q(user_id=user_id) | Q(user_id="taiwa-bot"), session_id=session_id)
    comment_serializer = CommentModelSerializer(comment_result,many=True)
    response_data = {
        'comment_data': comment_serializer.data,
    }
    print(response_data)
    return Response(response_data)



