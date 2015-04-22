import logging
import os
import re
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users

#telephone check
telephoneExpression = \
   re.compile( r'^\(\d{3}\)\d{3}-\d{4}$' )

#Adoptee database table
class User(db.Model):
	firstName = db.StringProperty()
	lastName = db.StringProperty()
	email = db.EmailProperty()
	phone = db.PhoneNumberProperty()
	cat = db.StringProperty()

#Cat database table
class CatDb(db.Model):
	pic = db.BlobProperty(default = None)
	name = db.StringProperty() 
	description = db.StringProperty() 
	age = db.StringProperty()
	color = db.StringProperty()
	size = db.StringProperty()
	
#Cat database filtering
class Filter(webapp2.RequestHandler):

	def post(self):
		#count to check if nothing was selected if so no filter
		count=0
		
		if (self.request.get('age')!= 'AGE'):
			self.AgeFilter()
		else:
			count=count+1
			
		if (self.request.get('color')!= 'COLOR'):
			self.ColorFilter()
		else:
			count=count+1
			
		if (self.request.get('size')!= 'SIZE'):
			self.SizeFilter()
		else:
			count=count+1
			
		if count == 3:
			self.NoFilter()
				
	#AGE filter
 	def AgeFilter(self):
		
		cat_query=db.Query(CatDb)
		age = self.request.get('age') 
		cat_query = cat_query.filter('age =', age)
		cat_list = cat_query.fetch(10)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
		self.response.out.write(template.render(path, {'cat_list': cat_list}))
		
	#COLOR filter
	def ColorFilter(self):
	
		cat_query=db.Query(CatDb)
		color=self.request.get('color')
		cat_query = cat_query.filter('color =', color)
		cat_list = cat_query.fetch(10)
		path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
		self.response.out.write(template.render(path, {'cat_list' : cat_list}))
		
	#SIZE filter	
	def SizeFilter(self):
		
		cat_query=db.Query(CatDb)
		size= self.request.get('size')
		cat_query = cat_query.filter('size =', size)
		cat_list = cat_query.fetch(10)
		path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
		self.response.out.write(template.render(path, {'cat_list' : cat_list}))
		
	#NO filter	
	def NoFilter(self):
		
		cat_list = CatDb.all()
		path = os.path.join(os.path.dirname(__file__),'templates/home.html')
		self.response.write(template.render(path,{"cat_list":cat_list}))
		
#MAIN PAGE
class MainPage(webapp2.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__),'templates/mainpage.html')
		self.response.write(template.render(path,{}))


class About(webapp2.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__),'templates/about.html')
		self.response.write(template.render(path,{}))
		
class Contact(webapp2.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__),'templates/contact.html')
		self.response.write(template.render(path,{}))
		
class Source(webapp2.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__),'templates/source.html')
		self.response.write(template.render(path,{}))
		
class MainCat(webapp2.RequestHandler):
	def get(self):
		
		#get user
		user = users.get_current_user()

		#If no user request
		if not user:		
			self.redirect(users.create_login_url(self.request.uri))
		
		#Put the Cat database in a dictionary
		cat_list = CatDb.all()
		path = os.path.join(os.path.dirname(__file__),'templates/home.html')
		self.response.write(template.render(path,{"cat_list":cat_list}))
		
#When the place cat for adoption button is pressed	
class Place(webapp2.RequestHandler):
	#GETS html file
	def get(self):
		path = os.path.join(os.path.dirname(__file__),'templates/inputCat.html')
		self.response.write(template.render(path,{}))
	
	#Creates cat in database and goes back home
	def post(self):
		c = CatDb()
		c.name = self.request.get("name")
		c.description = self.request.get("description")
		c.age = self.request.get("age")
		c.color = self.request.get("color")
		c.size = self.request.get("size")
		
		file_ = self.request.get("pic")
		if file_ is unicode:
			file_content = file_.encode('utf-8','replace')
		else:
			file_content = file_
		c.pic = db.Blob(file_content)
		
		c.put()
		
		cat_list = CatDb.all()
		path = os.path.join(os.path.dirname(__file__),'templates/home.html')
		self.response.write(template.render(path,{"cat_list":cat_list}))

#for displaying uploaded image of cats
class GetImage(webapp2.RequestHandler):
	def get(self):
		cat = db.get(self.request.get("entity_id"))
		if cat.pic:
			self.response.headers['Content-Type'] = "image/png"
			self.response.out.write(cat.pic)
		
#When the adopt button is pressed
class Adopt(webapp2.RequestHandler):

	def get(self):
	
		#grabbing name and key of cat
		catName = self.request.get("catName")
		catKey = self.request.get("catKey")	
		
		#Put in dictionary
		cat_l = {'name' : catName, 'key' : catKey} 
			
		path = os.path.join(os.path.dirname(__file__),'templates/adopt.html')
		self.response.write(template.render(path,{"cat_l":cat_l }))

#Displaying all adoptees in database
class Adoptees(webapp2.RequestHandler):

	def get(self):
		
		person_list = User.all()
		path = os.path.join(os.path.dirname(__file__),'templates/adoptees.html')
		self.response.write(template.render(path,{"person_list": person_list}))
		
#When they submit an adoption application
class Reply(webapp2.RequestHandler):
		
	def post(self):

		global personInfo
		personInfo = { 'firstName' : self.request.get("firstname"),
                  'lastName' : self.request.get("lastname"),
                  'email' : self.request.get("email"),
                  'phone' : self.request.get("phone"),
                  'cat' : self.request.get("catName")}
		
		registration = User(firstName=personInfo['firstName'],lastName=personInfo['lastName'],email=personInfo['email'],phone=personInfo['phone'],cat=personInfo['cat'])

		person_list = User.all()		
		
		for item in personInfo:
			if (telephoneExpression.match( personInfo[ 'phone' ] )):
				registration.put()				
				self.success()	
				break				
			else:
				self.printPhoneError()
				break		


	def success(self):
		#if successful adoption then delete cat from database
		cat = db.get(self.request.get("key"))
		db.delete(cat)
		
		path = os.path.join(os.path.dirname(__file__),'templates/hi.html')
		self.response.write(template.render(path,{}))

	def printPhoneError(self):

		path = os.path.join(os.path.dirname(__file__),'templates/printPhoneError.html')
		self.response.write(template.render(path,{}))
		

application = webapp2.WSGIApplication([('/',MainPage),('/cat',MainCat),('/adopt',Adopt),('/reply',Reply),('/place',Place),('/Filter',Filter),('/adoptees',Adoptees),('/img',GetImage),('/me',About),('/contact',Contact),('/source',Source)],debug=True)

