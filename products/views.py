from django.shortcuts import render, get_object_or_404, redirect
from datetime import date, timedelta
import uuid
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator
from django.db.models import Avg

from .models import (
    Product,
    Category,
    Order,
    OrderItem,
    OrderStatusHistory,
    Review,
    Wishlist,
)


def product_list(request):

    search_query = request.GET.get(
        "search",
        ""
    )

    category_id = request.GET.get(
        "category",
        ""
    )

    sort = request.GET.get(
        "sort",
        ""
    )

    products = Product.objects.all()

    categories = Category.objects.all()

    if search_query:
        products = products.filter(
            name__icontains=search_query
        )

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    if sort == "price_low":
        products = products.order_by("price")

    elif sort == "price_high":
        products = products.order_by("-price")

    elif sort == "newest":
        products = products.order_by("-created_at")

    elif sort == "name":
        products = products.order_by("name")

    paginator = Paginator(
        products,
        8
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        "products/product_list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_id,
            "selected_sort": sort,
        }
    )

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    reviews = Review.objects.filter(
        product=product
    ).order_by("-created_at")

    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    review_count = reviews.count()

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "average_rating": average_rating,
            "review_count": review_count,
        }
    )
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart_data = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    current_quantity = cart_data.get(
        product_id,
        0
    )

    if current_quantity < product.stock:

        cart_data[product_id] = (
            current_quantity + 1
        )

        request.session["cart"] = cart_data

    return redirect("cart")


def remove_from_cart(request, product_id):

    cart_data = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart_data:

        del cart_data[product_id]

    request.session["cart"] = cart_data

    return redirect("cart")


def cart(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    items = []

    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        subtotal = product.price * quantity

        total += subtotal

        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(
        request,
        "products/cart.html",
        {
            "items": items,
            "total": total,
        }
    )


def increase_quantity(request, product_id):

    cart_data = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart_data:

        product = get_object_or_404(
            Product,
            id=product_id
        )

        if cart_data[product_id] < product.stock:

            cart_data[product_id] += 1

    request.session["cart"] = cart_data

    return redirect("cart")


def decrease_quantity(request, product_id):

    cart_data = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart_data:

        if cart_data[product_id] > 1:

            cart_data[product_id] -= 1

        else:

            del cart_data[product_id]

    request.session["cart"] = cart_data

    return redirect("cart")


def checkout(request):


    cart_data = request.session.get(
        "cart",
        {}
    )
    if not cart_data:
        return redirect("cart")

    items = []
    total = 0


    # Get cart products

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )


        # Check stock before checkout

        if quantity > product.stock:

            return render(
                request,
                "products/checkout.html",
                {
                    "items": items,
                    "total": total,
                    "error":
                    f"{product.name} has only {product.stock} items in stock."
                }
            )


        subtotal = product.price * quantity

        total += subtotal


        items.append({

            "product": product,

            "quantity": quantity,

            "subtotal": subtotal,

        })


    # Create order

    if request.method == "POST":


        order = Order.objects.create(

            customer=(
                request.user
                if request.user.is_authenticated
                else None
            ),

            customer_name=request.POST.get(
                "customer_name"
            ),

            email=request.POST.get(
                "email"
            ),

            phone=request.POST.get(
                "phone"
            ),

            address=request.POST.get(
                "address"
            ),

            city=request.POST.get(
                "city"
            ),

            pincode=request.POST.get(
                "pincode"
            ),

            total_amount=total,
            
            estimated_delivery=date.today() + timedelta(days=5),
            
            tracking_number=f"TRK-{uuid.uuid4().hex[:8].upper()}",

            status="Pending",

            payment_status="Pending",

        )

        OrderStatusHistory.objects.create(
    order=order,
    status=order.status
)
        # Create order items
        # and reduce stock

        for item in items:

            product = item["product"]

            quantity = item["quantity"]


            OrderItem.objects.create(

                order=order,

                product=product,

                quantity=quantity,

                price=product.price,

            )


            # Reduce product stock

            product.stock -= quantity

            product.save()


        # Go to payment

        return redirect(

            "payment",

            order_id=order.id

        )


    return render(

        request,

        "products/checkout.html",

        {

            "items": items,

            "total": total,

        }

    )

def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    items = OrderItem.objects.filter(
        order=order
    )

    order_items = []

    for item in items:

        subtotal = item.price * item.quantity

        order_items.append({

            "product": item.product,

            "quantity": item.quantity,

            "subtotal": subtotal,

        })


    return render(
        request,
        "products/order_success.html",
        {
            "order": order,
            "items": order_items,
        }
    )


def register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        email = request.POST.get(
            "email"
        )

        password = request.POST.get(
            "password"
        )

        confirm_password = request.POST.get(
            "confirm_password"
        )


        if password != confirm_password:

            return render(
                request,
                "products/register.html",
                {
                    "error":
                    "Passwords do not match."
                }
            )


        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "products/register.html",
                {
                    "error":
                    "Username already exists."
                }
            )


        user = User.objects.create_user(

            username=username,

            email=email,

            password=password

        )

        login(
            request,
            user
        )

        return redirect(
            "product_list"
        )


    return render(
        request,
        "products/register.html"
    )


def user_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )


        user = authenticate(

            request,

            username=username,

            password=password

        )


        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "product_list"
            )


        return render(
            request,
            "products/login.html",
            {
                "error":
                "Invalid username or password."
            }
        )


    return render(
        request,
        "products/login.html"
    )


def user_logout(request):

    logout(request)

    return redirect(
        "product_list"
    )


def my_orders(request):

    if not request.user.is_authenticated:

        return redirect("login")


    orders = Order.objects.filter(

        customer=request.user

    ).prefetch_related(

        "orderitem_set__product"

    ).order_by(

        "-created_at"

    )


    for order in orders:

        for item in order.orderitem_set.all():

            item.subtotal = (
                item.price *
                item.quantity
            )


    return render(

        request,

        "products/my_orders.html",

        {
            "orders": orders,
        }

    )
def order_detail(request, order_id):

    if not request.user.is_authenticated:
        return redirect("login")

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    items = OrderItem.objects.filter(
        order=order
    ).select_related(
        "product"
    )

    order_items = []

    for item in items:

        subtotal = item.price * item.quantity

        order_items.append({
            "product": item.product,
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": subtotal,
        })

    return render(
        request,
        "products/order_detail.html",
        {
            "order": order,
            "items": order_items,
        }
    )
    
def order_tracking(request, order_id):

    if not request.user.is_authenticated:
        return redirect("login")

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    statuses = [
        "Pending",
        "Confirmed",
        "Packed",
        "Shipped",
        "Out for Delivery",
        "Delivered",
    ]

    current_status = order.status

    if current_status in statuses:
        current_index = statuses.index(current_status)
    else:
        current_index = -1

    tracking_steps = []

    for index, status in enumerate(statuses):

        if index < current_index:
            step_status = "completed"

        elif index == current_index:
            step_status = "current"

        else:
            step_status = "pending"

        tracking_steps.append({
            "name": status,
            "status": step_status,
        })

    return render(
        request,
        "products/order_tracking.html",
        {
            "order": order,
            "tracking_steps": tracking_steps,
        }
    )

def payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )


    if request.method == "POST":

        payment_method = request.POST.get(
            "payment_method"
        )


        # UPI

        if payment_method == "UPI":

            upi_id = request.POST.get(
                "upi_id"
            )


            if not upi_id:

                return render(

                    request,

                    "products/payment.html",

                    {
                        "order": order,

                        "error":
                        "Please enter your UPI ID."
                    }

                )


            order.payment_status = "Paid"

            order.status = "Confirmed"


        # Card

        elif payment_method == "Card":

            card_number = request.POST.get(
                "card_number"
            )

            expiry = request.POST.get(
                "expiry"
            )

            cvv = request.POST.get(
                "cvv"
            )


            if (
                not card_number
                or not expiry
                or not cvv
            ):

                return render(

                    request,

                    "products/payment.html",

                    {
                        "order": order,

                        "error":
                        "Please enter all card details."
                    }

                )


            order.payment_status = "Paid"

            order.status = "Confirmed"


        # Cash on Delivery

        elif payment_method == "COD":

            order.payment_status = "Pending"

            order.status = "Confirmed"


        # Invalid payment method

        else:

            return render(

                request,

                "products/payment.html",

                {
                    "order": order,

                    "error":
                    "Please select a payment method."
                }

            )


        order.save()


        request.session["cart"] = {}


        return redirect(

            "order_success",

            order_id=order.id

        )


    return render(

        request,

        "products/payment.html",

        {
            "order": order,
        }

    )

def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    # Only the owner can cancel the order

    if (
        request.user.is_authenticated
        and order.customer != request.user
    ):
        return redirect("my_orders")


    # Only Pending or Confirmed orders can be cancelled

    if order.status in ["Pending", "Confirmed"]:

        items = OrderItem.objects.filter(
            order=order
        )


        # Return products to stock

        for item in items:

            product = item.product

            product.stock += item.quantity

            product.save()


        # Cancel the order

        order.status = "Cancelled"

        order.save()


    return redirect("my_orders")

def add_review(request, product_id):

    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        # Check if user already reviewed this product

        existing_review = Review.objects.filter(
            product=product,
            user=request.user
        ).exists()

        if existing_review:

            return redirect(
                "product_detail",
                product_id=product.id
            )

        if rating and comment:

            Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=comment
            )

    return redirect(
        "product_detail",
        product_id=product.id
    )
    
def edit_review(request, review_id):

    if not request.user.is_authenticated:
        return redirect("login")

    review = get_object_or_404(
        Review,
        id=review_id
    )

    # Only the review owner can edit it
    if review.user != request.user:
        return redirect(
            "product_detail",
            product_id=review.product.id
        )

    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:

            review.rating = int(rating)
            review.comment = comment
            review.save()

            return redirect(
                "product_detail",
                product_id=review.product.id
            )

    return render(
        request,
        "products/edit_review.html",
        {
            "review": review,
        }
    )
    
def delete_review(request, review_id):

    if not request.user.is_authenticated:
        return redirect("login")

    review = get_object_or_404(
        Review,
        id=review_id
    )

    # Only the review owner can delete it
    if review.user != request.user:
        return redirect(
            "product_detail",
            product_id=review.product.id
        )

    product_id = review.product.id

    if request.method == "POST":
        review.delete()

    return redirect(
        "product_detail",
        product_id=product_id
    )
    
def add_to_wishlist(request, product_id):

    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(
        "product_detail",
        product_id=product.id
    )
    
def wishlist(request):

    if not request.user.is_authenticated:
        return redirect("login")

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        "product"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "products/wishlist.html",
        {
            "wishlist_items": wishlist_items,
        }
    )
    
def remove_from_wishlist(request, wishlist_id):

    if not request.user.is_authenticated:
        return redirect("login")

    wishlist_item = get_object_or_404(
        Wishlist,
        id=wishlist_id,
        user=request.user
    )

    wishlist_item.delete()

    return redirect("wishlist")