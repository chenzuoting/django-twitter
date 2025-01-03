from friendships.models import Friendship


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # Return list of users

        # Wrong 1: N + 1 queries issue
        # filer cost one query
        # for loop on each friendship cost N queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # Wrong 2:
        # Used JOIN, join friendship table and user table
        # Don't use JOIN in large DB
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # Correct 1:
        # Manually fileter id, use IN Query to search
        # from_user_id already exist in the table, no extra query required
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # Correct 2:
        # Use prefetch_related, will merge to 2 statements, use IN Query to search
        # Same as Correct 1, use 2 queries
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

        # Another simpler way is to return user_id instead of user
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
