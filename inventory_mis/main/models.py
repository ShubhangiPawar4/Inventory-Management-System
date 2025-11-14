
# Create your models here.
# main/models.py
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# --- Master Data Models ---

class Vendor(models.Model):
    """
    Represents a vendor or supplier of products.
    """
    full_name = models.CharField(max_length=50)
    address = models.TextField(blank=True)
    mobile = models.CharField(max_length=15)
    status = models.BooleanField(default=True) # A flag to indicate if the vendor is active

    class Meta:
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return self.full_name

class Unit(models.Model):
    """
    Represents the unit of measurement for a product (e.g., Pcs, Kg, Ltr).
    """
    title = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name_plural = 'Units'

    def __str__(self):
        return self.title

class Product(models.Model):
    """
    Represents a product in the inventory.
    """
    title = models.CharField(max_length=50)
    detail = models.TextField(blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="product/", blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title

class Customer(models.Model):
    """
    Represents a customer who purchases products.
    """
    customer_name = models.CharField(max_length=50)
    customer_mobile = models.CharField(max_length=15, blank=True)
    customer_address = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.customer_name

# --- Transactional Models ---

class Purchase(models.Model):
    """
    Records a purchase transaction.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    quantity = models.FloatField()
    price = models.FloatField()
    total_amount = models.FloatField(editable=False)
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Purchases'

    def save(self, *args, **kwargs):
        # Automatically calculate the total amount before saving
        self.total_amount = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase of {self.product.title} on {self.purchase_date.strftime('%Y-%m-%d')}"

class Sale(models.Model):
    """
    Records a sales transaction.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    quantity = models.FloatField()
    price = models.FloatField()
    total_amount = models.FloatField(editable=False)
    sale_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Sales'

    def save(self, *args, **kwargs):
        # Automatically calculate the total amount before saving
        self.total_amount = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.product.title} on {self.sale_date.strftime('%Y-%m-%d')}"

# --- Inventory and Signals ---

class Inventory(models.Model):
    """
    Tracks the total balance of each product.
    This model is updated automatically via signals.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_balance_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = 'Inventory'

    def __str__(self):
        return f"Inventory for {self.product.title}"

# Signals to update the inventory whenever a purchase or sale is made
@receiver(post_save, sender=Purchase)
def update_inventory_from_purchase(sender, instance, created, **kwargs):
    if created:
        inventory, _ = Inventory.objects.get_or_create(product=instance.product)
        inventory.total_balance_quantity += instance.quantity
        inventory.save()

@receiver(post_delete, sender=Purchase)
def remove_from_inventory_on_purchase_delete(sender, instance, **kwargs):
    inventory = Inventory.objects.get(product=instance.product)
    inventory.total_balance_quantity -= instance.quantity
    inventory.save()

@receiver(post_save, sender=Sale)
def update_inventory_from_sale(sender, instance, created, **kwargs):
    if created:
        inventory = Inventory.objects.get(product=instance.product)
        inventory.total_balance_quantity -= instance.quantity
        inventory.save()

@receiver(post_delete, sender=Sale)
def add_to_inventory_on_sale_delete(sender, instance, **kwargs):
    inventory = Inventory.objects.get(product=instance.product)
    inventory.total_balance_quantity += instance.quantity
    inventory.save()
