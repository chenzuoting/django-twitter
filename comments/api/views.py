from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from comments.api.permissions import IsObjectOwner
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)


class CommentViewSet(viewsets.GenericViewSet):
    # Only implement list, create, update, destroy
    # Not support retrieve
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    # Pre-defined functions
    # POST /api/comments/ -> create()
    # GET /api/comments/ -> list()
    # GET /api/comments/1/ -> retrieve()
    # DELETE /api/comments/1/ -> destroy()
    # PATCH /api/comments/1/ -> partial_update()
    # PUT /api/comments/1/ -> update()

    def get_permissions(self):
        # Use AllowAny() / IsAuthenticated() which instantiate an object
        # Not AllowAny / IsAuthenticated, it's just class name
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        # Another way to pass info to serializer: create a dict
        # Previously we are passing request
        data = {
            # use user from request, not from request.data
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # Need to specify data, otherwise it's instance by default
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save will trigger create in serializer
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # get_object will check whether it's exist, and return 404 if not exist
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            # instance is passed, serializer using update instead of create
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save will trigger update or create depending on whether argument instance being passed
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # In DRF, 'status code = 204 no content' is the default return value for destroy
        # But we return success=True to front end, so use 200
        return Response({'success': True}, status=status.HTTP_200_OK)