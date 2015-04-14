import pymongo 

class PMCConnection:
	
	def __init__(self, database_name, **keywords):
		try:
			if not keywords:
				self.connection = pymongo.MongoClient()
			else:
				self.host = keywords.get('host')
				self.port = keywords.get('port')
				self.connection = pymongo.MongoClient(self.host, self.port)
			print('Connected to MongoDB successfully!')
			self.database_name = database_name
		except:
			print('Could not connect to MongoDB: %s' % e) 
		
		self.db = self.connection[self.database_name]  #create a new database if not exist
		
		
	def addDocumentToCollection(self, collection, documentObj):
		#create a new collection if not exist
		self.collection = self.db[collection]
		cr = self.collection.find({'_id':documentObj.dc['_id']})
		if cr.count() == 0:
			self.collection.insert(documentObj.dc)
		else:
			self.collection.update({'_id':documentObj.dc['_id']},{'$set':{key:value for key,value in documentObj.dc.items() if key != '_id'}})
		documentObj.collection = self.collection
			