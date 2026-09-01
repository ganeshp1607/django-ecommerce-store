from django.contrib import admin

from .models import (
    Product,
    Category,
    Order,
    OrderItem,
    OrderStatusHistory,
    Wishlist,
)


admin.site.register(Wishlist)
admin.site.register(Category)
admin.site.register(Product)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    ordering = (
        "-created_at",
    )


class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        old_status = None

        if change:

            old_order = Order.objects.get(
                pk=obj.pk
            )

            old_status = old_order.status

        super().save_model(
            request,
            obj,
            form,
            change
        )

        if not change or old_status != obj.status:

            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status
            )

    list_display = (
        "id",
        "customer",
        "customer_name",
        "total_amount",
        "status",
        "payment_status",
        "estimated_delivery",
        "tracking_number",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "email",
        "phone",
        "tracking_number",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        OrderItemInline
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
    )

    search_fields = (
        "product__name",
    )

