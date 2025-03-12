from django.db import models
from django.contrib.auth.models import User

class CustomerSupplier(models.Model):
    CUSTOMER = 0
    SUPPLIER = 1
    BOTH = 2
    PARTNER_TYPE_CHOICES = [
        (CUSTOMER, "Cliente"),
        (SUPPLIER, "Fornecedor"),
        (BOTH, "Ambos"),
    ]

    type = models.IntegerField(choices=PARTNER_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=20, null=True, blank=True)
    cpf = models.CharField(max_length=20, null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    phone1 = models.CharField(max_length=50, null=True, blank=True)
    phone2 = models.CharField(max_length=50, null=True, blank=True)
    marital_status = models.CharField(max_length=30, null=True, blank=True)
    profession = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    
    # Endereço
    street = models.CharField(max_length=100, null=True, blank=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=20, null=True, blank=True)
    complement = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    date_birth = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_supplier_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_supplier_user_updated', verbose_name="Atualizado por")

    class Meta:
        verbose_name = 'Fornecedores Cliente'
        db_table = 'customer_suppliers'

    def __str__(self):
        return self.name
