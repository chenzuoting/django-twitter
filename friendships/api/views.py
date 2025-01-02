from pickle import FALSE

from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # POST /api/friendship/1/follow is to follow user with user_id=1
    # queryset should be User.objects.all() here
    # so that detail=True actions can check if pk (primary key) is existing
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk)
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers' : serializer.data},
            status=status.HTTP_200_OK
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk)
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'followings' : serializer.data},
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # Check if pk exist
        # self.get_object()

        # If already followed, return success and duplicated
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success' : True,
                'duplicated' : True,
            }, status=status.HTTP_201_CREATED)

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # Check if pk exist
        unfollow_user = self.get_object()
        # pk is str, convert to int
        # if request.user.id == int(pk):
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # delete() return two values, 1) # of data deleted, 2) # of data deleted for each type
        # Don't use on_delete=models.CASCADE, because this can delete lots of data, it's risky
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({'success': True, 'deleted': deleted})

    # More restful way to access followings / followers:
    # /api/friendships/?user_id=4&type=followings
    # /api/friendships/?user_id=4&type=followers
    def list(self, request, *args, **kwargs):
        if 'user_id' not in request.query_params:
            return Response('Missing user_id', status=400)

        type = request.query_params['type']
        user_id = request.query_params['user_id']

        if type == 'followers':
            friendships = Friendship.objects.filter(to_user_id=user_id).order_by('-created_at')
            serializer = FollowerSerializer(friendships, many=True)
            return Response(
                {'followers': serializer.data},
                status=status.HTTP_200_OK
            )
        elif type == 'followings':
            friendships = Friendship.objects.filter(from_user_id=user_id).order_by('-created_at')
            serializer = FollowingSerializer(friendships, many=True)
            return Response(
                {'followings': serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(f'Invalid type: {type}', status=400)

