from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("auction/new/", views.new_auction, name="newauction"),
    path("listing/<str:item_id>", views.listing, name="listing"),
    path("auction/watchlist/add/<str:item_id>/",
         views.handle_watchlist, name="handlewatchlist"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("auction/close/<str:item_id>/",
         views.close_listing, name="closelisting"),
    path("auction/comment/<str:item_id>", views.handle_comment, name="comment"),
    path("categories/", views.categories, name="categories"),
    path("category/<str:cat_id>", views.handle_category, name="category")
]
