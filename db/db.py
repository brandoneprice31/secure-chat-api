import json
import datetime
from pymongo import MongoClient
from bson import ObjectId

from config.config import Config

class DB:

    def __init__(self):
        self.config = Config()
        self.db = MongoClient(self.config.dbURI)[self.config.dbName]

    # Users

    def findUserById(self, id):
        return self.deserialize(self.db['users'].find_one({ '_id': ObjectId(id) }))

    def insertUser(self, user):

        user = {
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'apn_token': user['apn_token'],
            'session_token' : user['session_token']
        }

        return self.deserialize(self.db['users'].insert(user))

    def updateUserSessionToken(self, user_id, sessionToken):
        return self.deserialize(self.db['users'].update({ '_id': ObjectId(user_id)}, { '$set': { 'session_token': sessionToken } }))

    def findUsersByIds(self, user_ids):
        return self.deserialize(list(self.db['users'].find({ '_id': { '$in': [ObjectId(user_id) for user_id in user_ids] } }, { 'session_token': 0 })))

    def removeUserById(self, user_id):
        return self.deserialize(self.db['users'].update({ '_id': ObjectId(user_id)}, { '$set': { 'apn_token': None, 'deleted': True,'session_token': None } }))

    def updateUserById(self, user_id, first_name, last_name):
        return self.deserialize(self.db['users'].update({ '_id': ObjectId(user_id)}, { '$set': { 'first_name': first_name, 'last_name': last_name } }))

    def removeUserFromChat(self, user_id, chat_id):
        return self.deserialize(self.db['users'].update({ '_id': ObjectId(user_id)}, { '$push': { 'removed_chat_ids': ObjectId(chat_id) } }))

    # Chats

    def findChatById(self, id):
        return self.deserialize(self.db['chats'].find_one({ '_id': ObjectId(id) }))

    def insertChat(self, chat):
        mongo_user_ids = [ObjectId(user_id) for user_id in chat['user_ids']]
        return self.deserialize(self.db['chats'].insert({ 'user_ids':  mongo_user_ids }))

    def findChatsByUserId(self, user_id):
        query = {
            'user_ids': {
                '$elemMatch': {
                    '$eq': ObjectId(user_id)
                }
            }
        }

        return self.deserialize(list(self.db['chats'].find(query)))

    def updateChat(self, id, title):
        return self.deserialize(self.db['chats'].update({ '_id': ObjectId(id) }, { '$set': { 'title': title } }))

    def addUsersToChat(self, id, userIds):
        objectIds = [ObjectId(userId) for userId in userIds]
        return self.deserialize(self.db['chats'].update({ '_id' : ObjectId(id) }, { '$push' : { 'user_ids' : { '$each' : objectIds } } }))

    # Messages

    def insertMessage(self, user_id, chat_id, message):
        return self.deserialize(self.db['messages'].insert({ 'user_id': ObjectId(user_id), 'chat_id': ObjectId(chat_id), 'message': message, 'timestamp': datetime.datetime.utcnow() }))

    def findMessagesByChatId(self, chat_id):
        return self.deserialize(list(self.db['messages'].find({ 'chat_id': { '$eq': ObjectId(chat_id) } })))

    # Helpers

    def deserialize(self, object):
        return json.loads(JSONEncoder().encode(object))


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


db = DB()
