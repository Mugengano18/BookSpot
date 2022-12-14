from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import *

urlpatterns = [

    path('', home, name='home'),
    path("products/", product, name="store"),
    path("about/", about, name="about_us"),
    path("contacts/", contact, name="contact_us"),
    path('products/<str:pk>/', viewBook, name="single_book"),
    # ----------------------------------------------------------------------------------------
    path('cart/', cart, name="cart"),
    path('checkout/', checkout, name="checkout"),
    #  ------------------------------------------------------------------------------------------------------
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('user_register/', register, name='register'),
    path('book_register/', book_register, name='book_register'),
    path('update_item/', updateItem, name='update_item'),
    path('dashboard/', Dashboard, name='dashboard'),
]
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
