import logging
from spotipy.cache_handler import CacheHandler
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import update 

from db import User, metadata

logger = logging.getLogger(__name__)
class DBCacheHandler(CacheHandler):
    """
    A cache handler that stores(not tested) and retrieves token from da sqlalchemy database with and 
    a specified User
    """

    def __init__(self, db, user):
        self.db = db
        self.user = user

    def get_cached_token(self):
        token_info = None
        try:
            token_info = self.user.token
        except KeyError:
            logger.debug("Token not found in the session")

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            session = SQLSession(self.db)
            stmt = (
                update(User)
                .where(User.username == self.user.username)
                .values(token=token_info)
                .execution_options(synchronize_session=False)
            )
            session.execute(stmt)
            session.close()
        except Exception as e:
            logger.warning("Error saving token to cache: " + str(e))
