from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('contact/',views.contact,name='contact'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('change_password/',views.change_password,name='change_password'),
    path('seller_change_password/',views.seller_change_password,name='seller_change_password'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('new_password/',views.new_password,name='new_password'),
    path('profile/',views.profile,name='profile'),
    path('seller_profile/',views.seller_profile,name='seller_profile'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('seller_add_book/',views.seller_add_book,name='seller_add_book'),
    path('seller_view_book/',views.seller_view_book,name='seller_view_book'),
    path('seller_book_detail/<int:pk>/',views.seller_book_detail,name='seller_book_detail'),
    path('seller_book_edit/<int:pk>/',views.seller_book_edit,name='seller_book_edit'),
    path('seller_book_delete/<int:pk>/',views.seller_book_delete,name='seller_book_delete'),
    path('user_view_book/<str:cs>/',views.user_view_book,name='user_view_book'),
    path('user_book_detail/<int:pk>/',views.user_book_detail,name='user_book_detail'),
    path('add_to_wishlist/<int:pk>',views.add_to_wishlist,name='add_to_wishlist'),
    path('mywishlist/',views.mywishlist,name='mywishlist'),
    path('remove_from_wishlist/<int:pk>',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('add_to_cart/<int:pk>',views.add_to_cart,name='add_to_cart'),
    path('mycart/',views.mycart,name='mycart'),
    path('remove_from_cart/<int:pk>',views.remove_from_cart,name='remove_from_cart'),
    path('change_qty/<int:pk>/',views.change_qty,name='change_qty'),
    path('pay/',views.initiate_payment,name="pay"),
    path('callback/', views.callback, name='callback'),
    path('ajax/validate_email/',views.validate_email,name='validate_email'),
    path('ajax/validate_email_signup/',views.validate_email_signup,name='validate_email_signup'),
]
