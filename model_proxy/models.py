
from base_models.models import CustomUser, Product


# Create proxy models for CustomUser and Product
class CustomUserProxy(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Custom User Proxy"
        verbose_name_plural = "Custom User Proxies"
        ordering = ["username"]
        # Add any additional options you need here
        # For example, you can specify a different database table name


class ProductProxy(Product):
    class Meta:
        proxy = True
        verbose_name = "Product Proxy"
        verbose_name_plural = "Product Proxies"
        ordering = ["name"]
        # Add any additional options you need here
        # For example, you can specify a different database table name
        # db_table = "product_proxy"
    def get_discounted_price(self, discount_percentage):
        """
        Calculate the discounted price of the product.
        """
        discount_amount = (discount_percentage / 100) * self.price
        return self.price - discount_amount
