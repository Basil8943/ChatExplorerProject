from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from ChatExplorerApp.Models.chatmodel import ChatModel
import json
from ChatExplorerApp.Models.commentmodel import CommentModel
from ChatExplorerApp.Models.roles import RoleModel, UserRoleModel
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
from django.contrib.auth import logout
import uuid
from rest_framework import status
from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.errors import EncryptionError
from bson import json_util
from pathlib import Path
from django.conf import settings
from .create_key import create_key


# Create your views here.


def index(request):
    invalid_login = False
    user_role=RoleModel.objects.all()
    # RoleModel.objects.create(rollname="User")
    # RoleModel.objects.create(rollname="Expert Coach")
    request.session['user_roles'] = list(user_role.values())
    return render(request, "index.html", {'show_login_card': True, 'invalid_login': invalid_login, 'user_roles': request.session['user_roles']})



def save_to_db(request):
    #actual path of your CSV file
    create_key()
    file_path = './Files/ChatExport.json'
    try:

        secret_file = './Files/secret_key.txt'
        with open(secret_file, 'r') as file:
            key_hex = file.read()

        local_master_key = bytes.fromhex(key_hex)
        collection_schema = json_util.loads(Path("json_schema.json").read_text())


        kms_providers = {"local": {"key": local_master_key}}

        csfle_opts = AutoEncryptionOpts(
        kms_providers,
        "SecretkeyDb.__keystore",
        schema_map={"ChatExplorerDB.UserModel": collection_schema},
        )


        with open(file_path, 'r') as file:
            json_data = json.load(file)

        # # Loop through JSON data and save to the database
        # for item in json_data:
        #     chat_instance = ChatModel(
        #         sessionId=item['sessionId'],
        #         userId=item['userId'],
        #         messageId=item['messageId'],
        #         message=item['message'],
        #         createdAt=item['createdAt'],
        #         updatedAt=item['updatedAt'],
        #     )
        #     chat_instance.save()


        


        user_json_file = './Files/Users.json'
        with open(user_json_file, 'r') as file:
            data = json.load(file)  # Use json.load to load the JSON data


            with MongoClient(settings.CONNECTION_STRING, auto_encryption_opts=csfle_opts) as client:
                client.ChatExplorerDB.UserModel.delete_many({})
                

                for item in data:
                    client.ChatExplorerDB.UserModel.insert_one({
                        "userId": item["userId"],
                        "orgId": item["orgId"],
                        "email": item["email"],
                        "firstName": item["firstName"],
                        "lastName": item["lastName"],
                        "createdAt": item["createdAt"],
                        "updatedAt": item["updatedAt"],
                        "metadata": item["metadata"],
                    })
    except FileNotFoundError:
        print(f'File not found')
    except json.JSONDecodeError:
        print(f'Invalid JSON format in the file')
        

    return HttpResponse("Data saved to the database.")

# create new account
def signup(request):
    invalid_signup = False 
    # Check if the request method is POST (form submission)
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        role = int(request.POST['role'])# get it as int
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        # Check if the passwords match
        if password != cpassword:
            message = "Passwords do not match. Please enter the same password"
            print(message)
            invalid_signup=True
            return render(request, "index.html", {'invalid_signup': invalid_signup, 'message': message, 'show_signup_card': True})

        # Check if the email already exists
        try:
            # Attempt to get a user by email
            existing_user = User.objects.get(email=email)

            # If a user with the provided email exists, handle it
            if (existing_user):
                print("aa")
                message = "Email already exists"
                print(message)
                invalid_signup = True
                return render(request, "index.html", {'invalid_signup': invalid_signup, 'message': message, 'show_signup_card': True})

        except User.DoesNotExist:
            try:
                # Combine first name and last name to create a new username
                new_username = f"{firstname.lower()}{lastname.lower()}"

                # Check if the combined username already exists
                user_count = User.objects.filter(username__startswith=new_username).count()

                # If the combined username already exists, create a new unique username
                if user_count > 0:
                    new_username = f"{new_username}{user_count + 1}"
                
                # Get the selected role based on the provided role ID
                selected_role = RoleModel.objects.get(pk=role)

                print(selected_role, "Selected Role")


                # Create a new user
                user = User.objects.create_user(username=new_username, email=email, password=password, first_name=firstname, last_name=lastname)
                print(user.username, "User Created")

                # Create a new UserRoleModel entry for the user and assigned role
                UserRoleModel.objects.create(user_id=user.id, rolltype_id=role)

                # Get the role name for the user
                user_role = RoleModel.objects.get(id=role)
                request.session['rolltype_id'] = role

                # Optionally, you can log in the user after signup
                user = authenticate(request, username=new_username, password=password)
                print("User Authenticated:", user)

                if user is not None:
                    login(request, user)
                    print("User created and logged in.")

                    # Get user details for session data
                    first_name = request.user.first_name
                    last_name = request.user.last_name
                    full_name = f"{first_name} {last_name}"

                    # Set session data for the user
                    request.session['user_full_name'] = full_name
                    request.session['user_email'] = email
                    request.session['user_role'] = user_role.rollname
                    request.session['user_role_id'] = user_role.id


                    print("Logged in")

                    # Redirect to a chat page 
                    return redirect('ChatExplorerApp:chat')

            except Exception as e:
                print(f"Database error: {e}")
                # Handle the error, e.g., display an error message to the user
                return render(request, "index.html", {'error_message': 'An error occurred during signup.', 'show_signup_card': True})

    # If the request method is not POST, render the signup.html template
    return render(request, "index.html", {'show_signup_card': True})

# login
# Api Method for Getting All Session Data
def Userlogin(request):
    invalid_login = False 
    # Check if the request method is POST (form submission)
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Try to get the user object based on the provided email
        try:
            userObj = User.objects.get(email=email) #get email from UserModel
        except:
            invalid_login = True
            message = "Invalid email"
            return render(request, "index.html", {'invalid_login': invalid_login, 'message': message, 'show_login_card': True})

        # Try to authenticate the user
        try:
            # Handle authentication success
            user = authenticate(request, username=userObj.username, password=password)

            # get userroletype_id from UserRoleModel
            user_type = UserRoleModel.objects.get(user_id=user.id) 

            # get Rollname from RoleModel as Object
            user_roleObj = RoleModel.objects.get(id=user_type.rolltype_id)
            user_role = user_roleObj.rollname
            #save userrole to session
            request.session['user_role'] = user_role
            request.session['rolltype_id'] = user_type.rolltype_id


        except:
            # Handle authentication failure
            invalid_login = True
            message = "User not found"
            return render(request, "index.html", {'invalid_login': invalid_login, 'message': message, 'show_login_card': True})

        # Check if authentication was successful
        if user is not None:
            # Login the user
            login(request, user)
            print("User logged in.")
            # get firstname and lastname from user
            first_name = request.user.first_name
            last_name = request.user.last_name

            # merging firstname and lastname as fullname
            full_name = f"{first_name} {last_name}"
            # save fullname and email to session
            request.session['user_full_name'] = full_name
            request.session['user_email'] = email

            # Redirect to a chat page
            return redirect('ChatExplorerApp:chat')
        else:
            # Handle invalid login credentials
            print("Invalid login credentials.")
            invalid_login = True
            message = "User not found"
            return render(request, "index.html", {'invalid_login': invalid_login, 'message': message, 'show_login_card': True})

    # If the request method is not POST, render the signup.html template
    return render(request, "signup.html")

# Api Method for Getting All Session Data
@api_view(['GET'])
def getsessions(request,user_id):
    session_list = ChatModel.objects.filter(userId=user_id).values('sessionId').annotate(latest_created=Max('createdAt'))
    sessions_data = [{'sessionId': session['sessionId'], 'latest_created': session['latest_created']} for session in session_list]
    return JsonResponse(sessions_data, safe=False)


# Method for rendering the index view only if the user is logged in
@login_required(login_url='/')  # Redirect to '/' if the user is not logged in
def chat(request):
    # Retrieve all user objects from the UserModel
    # Retrieve user details from the session
    user_full_name = request.session.get('user_full_name', '')
    user_email = request.session.get('user_email', '')
    user_role = request.session.get('user_role', '')
    user_roletype_id = request.session.get('rolltype_id', '')
    user_list = fetch_data_from_db(user_roletype_id)
    
    # Create a dictionary with user details
    user_details = {
        'full_name': user_full_name,
        'email': user_email,
        'user_role': user_role,
        'roletype_id':user_roletype_id
    }

    # Render the 'chat.html' template with user_list and user_details as context
    return render(request, 'chat.html', {'user_list': user_list, 'user_details': user_details})




# Api Method for getting chat results with session_id and user_id
@api_view(['GET'])
def getchatresults(request,user_id,session_id):
    chat_result = ChatModel.objects.filter(Q(userId=user_id) | Q(userId="taiwa-bot"), sessionId=session_id)
    print(chat_result)
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
                    CommentModel.objects.create(comment=comment, session_id=session_id, user_id=user_id,commented_user_id=commented_user_id,response = None)
                    
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



@api_view(['POST'])
def save_response(request):
    if request.user.is_authenticated:
        response_user_id = request.user.id
    else:
        return Response({
        "message":"Authentication Failed",
        "status":False
        })
    try:
        response_text = request.data['response_text']
        comment_id = request.data['comment_id']
        exist_comment = CommentModel.objects.get(id = comment_id)
        respose_instance = {
                "response_id":str(uuid.uuid4()),
                "response_text":response_text,
                "response_user_id": response_user_id,
                "response_username":request.user.first_name + " " + request.user.last_name
            }
        print(f"ResponseInstance : {respose_instance}")
        if exist_comment.response is None:  
            exist_comment.response = [respose_instance]
        else:
            exist_comment.response.append(respose_instance)
        exist_comment.save()
        return Response({
            "message":"Successfully Saved",
            "status":True
        })
    except Exception as e:
        print(f"Exception:{e}")
        return Response({
            "message":"Error Occured While Saving",
            "status":False
        })

def userlogout(request):
    # Clear session data
    request.session.flush()
    # Logout the user
    logout(request)
    # Redirect to the desired URL
    return redirect("/")

## Delete Comment by passing CommentId and CommentParentID
@api_view(['POST'])
def delete_comment(request):
    try:
        parrent_comment_id = request.data["parrent_comment_id"]
        comment_id = request.data["child_comment_id"]
        if comment_id != '0':
            existed_comment = CommentModel.objects.get(id = parrent_comment_id)
            if existed_comment is not None:
                updated_response = [item for item in existed_comment.response if item.get("response_id") != comment_id]
                if len(existed_comment.response) != len(updated_response):
                    existed_comment.response = updated_response
                    existed_comment.save()
                    return Response({
                        "detail":"comment deleted successfully",
                        "status":True
                    })
                else:
                    return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            print(f"Parent{parrent_comment_id}")
            existed_comment = CommentModel.objects.get(id = parrent_comment_id)
            if existed_comment is not None:
                 existed_comment.delete()
                 return Response({
                        "detail":"comment deleted successfully",
                        "status":True,
                        "message":"success"
                    })
            else:
                 return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def fetch_data_from_db(role_id):
        if(role_id == 2):
            secret_file = './Files/secret_key.txt'
            with open(secret_file, 'r') as file:
                key_hex = file.read()

            local_master_key = bytes.fromhex(key_hex)
            collection_schema = json_util.loads(Path("json_schema.json").read_text())


            kms_providers = {"local": {"key": local_master_key}}

            csfle_opts = AutoEncryptionOpts(
            kms_providers,
            "SecretkeyDb.__keystore",
            schema_map={"ChatExplorerDB.UserModel": collection_schema},
            )

            with MongoClient(settings.CONNECTION_STRING, auto_encryption_opts=csfle_opts) as client:
                return list(client.ChatExplorerDB.UserModel.find())
        else:
            with MongoClient(settings.CONNECTION_STRING) as client:
                return list(client.ChatExplorerDB.UserModel.find())