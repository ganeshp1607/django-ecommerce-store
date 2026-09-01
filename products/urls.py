from django.urls import path

from .views import (
    product_list,
    product_detail,
    add_to_cart,
    remove_from_cart,
    cart,
    increase_quantity,
    decrease_quantity,
    checkout,
    order_success,
    order_detail,
    order_tracking,
    register,
    user_login,
    user_logout,
    my_orders,
    payment,
    cancel_order,
    add_review,
    edit_review,
    delete_review,
    add_to_wishlist,
    wishlist,
    remove_from_wishlist,
)


urlpatterns = [
    path("", product_list, name="product_list"),

    path(
        "product/<int:product_id>/",
        product_detail,
        name="product_detail"
    ),

    path(
        "cart/add/<int:product_id>/",
        add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:product_id>/",
        remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/",
        cart,
        name="cart"
    ),

    path(
        "cart/increase/<int:product_id>/",
        increase_quantity,
        name="increase_quantity"
    ),

    path(
        "cart/decrease/<int:product_id>/",
        decrease_quantity,
        name="decrease_quantity"
    ),

    path(
        "checkout/",
        checkout,
        name="checkout"
    ),

    path(
        "order-success/<int:order_id>/",
        order_success,
        name="order_success"
    ),
    path(
    "order/<int:order_id>/",
    order_detail,
    name="order_detail"
),
    path(
    "order/<int:order_id>/tracking/",
    order_tracking,
    name="order_tracking"
),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("my-orders/", my_orders, name="my_orders"),
    path(
    "payment/<int:order_id>/",
    payment,
    name="payment"),
    path(
    "order/cancel/<int:order_id>/",
    cancel_order,
    name="cancel_order"),
    path(
    "product/<int:product_id>/review/",
    add_review,
    name="add_review"),
            path(
    "review/<int:review_id>/edit/",
    edit_review,
    name="edit_review"
),

path(
    "review/<int:review_id>/delete/",
    delete_review,
    name="delete_review"
),
path(
    "wishlist/add/<int:product_id>/",
    add_to_wishlist,
    name="add_to_wishlist"
),
path(
    "wishlist/",
    wishlist,
    name="wishlist"
),
path(
    "wishlist/remove/<int:wishlist_id>/",
    remove_from_wishlist,
    name="remove_from_wishlist"
),

]