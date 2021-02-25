from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler

from apps.accounts.models import FacebookProfile
from apps.accounts.serializers import SocialSerializer, PageDetailsSerializer
from integrations.facebook_graph.client import FacebookGraphAPIClient


class UserAuthenticateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SocialSerializer(data=request.data)
        if serializer.is_valid():
            try:
                client = FacebookGraphAPIClient()
                user_details = client.get_user_details(serializer.validated_data['accessToken'])
                if user_details.get('id'):
                    if FacebookProfile.objects.filter(facebook_account_id=user_details['id']).exists():
                        authenticated_user = FacebookProfile.objects.get(facebook_account_id=user_details['id']).user
                        FacebookProfile.objects.filter(facebook_account_id=user_details['id']).update(
                            primary_access_token=serializer.validated_data['accessToken'])
                    else:
                        if User.objects.filter(email__iexact=user_details.get('email')).exists():
                            authenticated_user = User.objects.get(email__iexact=user_details.get('email'))
                        elif User.objects.filter(username=user_details.get('id')).exists():
                            authenticated_user = User.objects.get(username=user_details.get('id'))
                        else:
                            username = user_details.get('email', '') if user_details.get('email') else user_details[
                                'id']
                            password = User.objects.make_random_password()
                            data = {'email': user_details.get('email', ''), 'username': username,
                                    'first_name': user_details.get('first_name'),
                                    'last_name': user_details.get('last_name'),
                                    'password': password,
                                    'is_active': True}
                            authenticated_user = User.objects.create(**data)
                        FacebookProfile.objects.create(facebook_account_id=user_details['id'], user=authenticated_user,
                                                       primary_access_token=serializer.validated_data['accessToken'])
                    if authenticated_user and authenticated_user.is_active:
                        login(request, authenticated_user)
                        response = {
                            "token": jwt_encode_handler(jwt_payload_handler(authenticated_user))
                        }
                        return Response(status=status.HTTP_200_OK, data=response)
                else:
                    return Response({'message': "Token expired try again"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": {"accessToken": "Invalid token", }}, status=status.HTTP_400_BAD_REQUEST)


class FacebookPageListView(APIView):

    def get(self, request, *args, **kwargs):
        client = FacebookGraphAPIClient(user=request.user)
        page_list = client.get_user_accounts()
        return Response(status=status.HTTP_200_OK, data=page_list.get('data', []))


class FacebookPageView(APIView):
    serializer_class = PageDetailsSerializer

    def get(self, request, *args, **kwargs):
        client = FacebookGraphAPIClient(user=request.user)
        page_details = client.get_page_details(kwargs['id'])
        page_details = self.get_cleaned_response_data(page_details)
        return Response(status=status.HTTP_200_OK, data=page_details)

    def get_cleaned_response_data(self, page_details):
        if page_details.get('phone') is None:
            page_details['phone'] = ''
        if page_details.get('about') is None:
            page_details['about'] = ''
        if page_details.get('website') is None:
            page_details['website'] = ''
        if page_details.get('emails') is None:
            page_details['emails'] = ''
        elif page_details.get('emails'):
            page_details['emails'] = page_details['emails'][0]
        return page_details

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            client = FacebookGraphAPIClient(user=request.user)
            response = client.update_page_details(kwargs['id'], serializer.validated_data)
            if response.status_code == 200:
                return Response({'message': response.json()})
            else:
                return Response(response.json()['error'], status=response.status_code)
        if 'emails' in serializer.errors:
            return Response({'emails': serializer.errors['emails'][0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
