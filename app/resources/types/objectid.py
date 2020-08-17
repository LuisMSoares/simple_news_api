from bson.objectid import ObjectId


class ObjectIdType(object):
    @staticmethod
    def validate_objectid_type(value):
        try:
            ObjectId(value)
        except:
            return False
        else:
            return True

    def __call__(self, value):
        try:
            ObjectId(value)
        except:
            raise Exception(
                "'{}' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string".format(value))
        else:
            return value