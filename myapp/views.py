from django.shortcuts import render,redirect
from .models import Contact,User,Book,Wishlist,Cart,Transaction
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.mail import send_mail
import random
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

def validate_email(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	print(data)
	return JsonResponse(data)

def validate_email_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	print(data)
	return JsonResponse(data)

def initiate_payment(request):
    try:
        amount = int(request.POST['amount'])
        user=User.objects.get(email=request.session['email'])
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str("jigar93776@gmail.com")),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    carts=Cart.objects.filter(user=user)
    for i in carts:
    	i.payment_status="completed"
    	i.save()
    carts=Cart.objects.filter(user=user,payment_status="pending")
    request.session['cart_count']=len(carts)
    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def index(request):
	return render(request,'index.html')

def seller_index(request):
	return render(request,'seller_index.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
				name=request.POST['name'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				remarks=request.POST['remarks']
			)
		msg="Contact Saved Successfully"
		contacts=Contact.objects.all().order_by("-id")[:5]
		total_contact=len(Contact.objects.all())

		return render(request,'contact.html',{'msg':msg,'contacts':contacts,'total_contact':total_contact})
	else:
		contacts=Contact.objects.all().order_by("-id")[:5]
		total_contact=len(Contact.objects.all())
		return render(request,'contact.html',{'contacts':contacts,'total_contact':total_contact})

def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				#password=request.POST['password']
				#password=make_password(password)
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						gender=request.POST['gender'],
						address=request.POST['address'],
						password=request.POST['password'],
						cpassword=request.POST['cpassword'],
						image=request.FILES['image'],
						usertype=request.POST['usertype']
					)
				msg="SignUp Successfull"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})

	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
					email=request.POST['email'],
					password=request.POST['password']
				)
			if user.usertype=="user":
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['image']=user.image.url
				wishlists=Wishlist.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlists)
				carts=Cart.objects.filter(user=user)
				request.session['cart_count']=len(carts)
				return render(request,'index.html')

			elif user.usertype=="seller":
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['image']=user.image.url
				return render(request,'seller_index.html')
		except:
			msg="Email Or Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['wishlist_count']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])

		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.cpassword=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="Password & Confirm New Password Does Not Matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')

def seller_change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])

		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.cpassword=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="Password & Confirm New Password Does Not Matched"
				return render(request,'seller_change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'seller_change_password.html',{'msg':msg})
	else:
		return render(request,'seller_change_password.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			subject = 'OTP For Forgot Password'
			otp=random.randint(1000,9999)
			message = 'Your OTP For Forgot Password Is '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [request.POST['email'], ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'otp':otp,'email':request.POST['email']})
		except:
			msg="Email Does Not Exists"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def verify_otp(request):
	otp1=request.POST['otp1']
	otp2=request.POST['otp2']
	email=request.POST['email']

	if otp1==otp2:
		return render(request,'new_password.html',{'email':email})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'otp':otp1,'email':email,'msg':msg})

def new_password(request):
	email=request.POST['email']
	new_password=request.POST['new_password']	
	cnew_password=request.POST['cnew_password']

	user=User.objects.get(email=email)

	if new_password==cnew_password:
		user.password=new_password
		user.cpassword=new_password
		user.save()
		msg="Password Updated Successfully"
		return render(request,'login.html',{'msg':msg})
	else:
		msg="New Password & Confirm New Password Does Not Matched"
		return render(request,'new_password.html',{'email':email,'msg':msg})

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.email=request.POST['email']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		user.gender=request.POST['gender']
		try:
			user.image=request.FILES['image']
			user.save()
		except:
			pass
		user.save()
		msg="Profile Update Successfully"
		request.session['image']=user.image.url
		return render(request,'index.html')
	else:
		return render(request,'profile.html',{'user':user})

def seller_profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.email=request.POST['email']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		user.gender=request.POST['gender']

		try:
			user.image=request.FILES['image']
			user.save()
		except:
			pass
		user.save()
		msg="Profile Update Successfully"
		request.session['image']=user.image.url
		return render(request,'seller_index.html')
	else:
		return render(request,'seller_profile.html',{'user':user})

def seller_add_book(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Book.objects.create(
				seller=seller,
				book_category=request.POST['book_category'],
				book_name=request.POST['book_name'],
				book_price=request.POST['book_price'],
				book_quantity=request.POST['book_quantity'],
				book_author=request.POST['book_author'],
				book_description=request.POST['book_description'],
				book_image=request.FILES['book_image']
			)
		msg="Book Added Successfully"
		return render(request,'seller_add_book.html',{'msg':msg})
	else:
		return render(request,'seller_add_book.html')

def seller_view_book(request):
	seller=User.objects.get(email=request.session['email'])
	books=Book.objects.filter(seller=seller)
	return render(request,'seller_view_book.html',{'books':books})

def seller_book_detail(request,pk):
	book=Book.objects.get(pk=pk)
	return render(request,'seller_book_detail.html',{'book':book})

def seller_book_edit(request,pk):
	book=Book.objects.get(pk=pk)
	
	if request.method=="POST":
		book.book_name=request.POST['book_name']	
		book.book_price=request.POST['book_price']
		book.book_author=request.POST['book_author']
		book.book_quantity=request.POST['book_quantity']
		book.book_description=request.POST['book_description']
		try:
			book.book_image=request.FILES['book_image']
			book.save()
		except:
			pass
		book.save()
		return redirect("seller_view_book")
	else:
		return render(request,'seller_book_edit.html',{'book':book})

def seller_book_delete(request,pk):
	book=Book.objects.get(pk=pk)
	book.delete()
	return redirect("seller_view_book")

def user_view_book(request,cs):
	if cs=="all":
		books=Book.objects.all()
		return render(request,'user_view_book.html',{'books':books})
	else:
		books=Book.objects.filter(book_name=cs)
		return render(request,'user_view_book.html',{'books':books})

def user_book_detail(request,pk):
	flag=False
	flag1=False
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	try:
		Wishlist.objects.get(user=user,book=book)
		flag=True
	except:
		pass

	try:
		Cart.objects.get(user=user,book=book,payment_status="pending")
		flag1=True
	except:
		pass
	return render(request,'user_book_detail.html',{'book':book,'flag':flag,'flag1':flag1})

def mywishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'mywishlist.html',{'wishlists':wishlists})

def add_to_wishlist(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,book=book)
	return redirect('mywishlist')

def remove_from_wishlist(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,book=book)
	wishlist.delete()
	return redirect('mywishlist')

def mycart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status="pending")
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'mycart.html',{'carts':carts,'net_price':net_price})

def add_to_cart(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,book=book,price=book.book_price,total_price=book.book_price)
	return redirect('mycart')

def remove_from_cart(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,book=book)
	cart.delete()
	return redirect('mycart')

def change_qty(request,pk):
	cart=Cart.objects.get(pk=pk)
	qty=int(request.POST['qty'])
	cart.qty=qty
	cart.total_price=qty*cart.price
	cart.save()
	return redirect('mycart')