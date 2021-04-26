from django.db import models
from django.utils import timezone
# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	remarks=models.TextField()

	def __str__(self):
		return self.name

class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	gender=models.CharField(max_length=100)
	address=models.TextField()
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	image=models.ImageField(upload_to="images/",default="",blank=True,null=True)
	usertype=models.CharField(max_length=100,default="user")

	def __str__(self):
		return self.fname+" - "+self.lname

class Book(models.Model):

	CHOICES=(
		('programming','programming'),
		('novel','novel'),
		('gk','gk'),
		('comic','comic')
		)
	seller=models.ForeignKey(User,on_delete=models.CASCADE)
	book_category=models.CharField(max_length=100,choices=CHOICES)
	book_name=models.CharField(max_length=100)
	book_price=models.IntegerField()
	book_author=models.CharField(max_length=100)
	book_quantity=models.IntegerField()
	book_description=models.TextField()
	book_image=models.ImageField(upload_to="book_images/")

	def __str__(self):
		return self.seller.fname+" - "+self.book_name

class Wishlist(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	book=models.ForeignKey(Book,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.book.book_name


class Cart(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	book=models.ForeignKey(Book,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	qty=models.IntegerField(default=1)
	price=models.IntegerField()
	total_price=models.IntegerField()
	payment_status=models.CharField(max_length=100,default="pending")

	def __str__(self):
		return self.user.fname+" - "+self.book.book_name

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)