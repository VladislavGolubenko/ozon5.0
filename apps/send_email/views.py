from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .tasks import send_message


class Ser(serializers.Serializer):
    users = serializers.ListField(required=True)
    title = serializers.CharField(required=True)
    text = serializers.CharField(required=True)




class SendMessageEmail(APIView):
    """
    Пример body
    ```  
    {
    "users": [2,1,4,5],
    "title": "Hello",
    "text": "World"
    }```
    """
    serializer_class = Ser
    def post(self, request):
        users = request.data.get("users")
        title = request.data.get("title")
        text = request.data.get("text")
        if users is None:
            return Response(data={"users is not exist": "users is not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if title is None:
            return Response(data={"title is not exist": "title is not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if text is None:
            return Response(data={"text is not exist": "text is not exist"}, status=status.HTTP_400_BAD_REQUEST) 
        
        if isinstance(users, list) is False:
            return Response(data={"users not array": "users not array"}, status=status.HTTP_400_BAD_REQUEST)
        if len(users) == 0:
            return Response(data={"users is empty": "users is empty"}, status=status.HTTP_400_BAD_REQUEST)
        send_message.delay(title, text, users)
        return Response(status=status.HTTP_200_OK)
