from django.db import models
from django.contrib.auth.models import User

class TypeCustomerSupplier(models.Model):
    name = models.CharField('Nome', max_length=100)

    class Meta:
        verbose_name = 'Tipo de Fornecedores e Cliente'
        db_table = 'type_customer_suppliers'

    def __str__(self):
        return self.name
    

class CustomerSupplier(models.Model):
    type_customer_supplier = models.ManyToManyField(TypeCustomerSupplier, verbose_name='Tipo de cadastro')
    name = models.CharField('Nome ou Razão Social', max_length=100)
    cnpj = models.CharField('CNPJ', max_length=20, null=True, blank=True)
    cpf = models.CharField('CPF', max_length=20, null=True, blank=True)
    rg = models.CharField('RG', max_length=20, null=True, blank=True)
    phone1 = models.CharField('Telefone 1', max_length=50, null=True, blank=True) 
    phone2 = models.CharField('Telefone 2', max_length=50, null=True, blank=True)
    marital_status = models.CharField('Estado Civil', max_length=30, null=True, blank=True)
    profession = models.CharField('Profissão', max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    
    # Endereço
    street = models.CharField('Rua', max_length=100, null=True, blank=True)
    neighborhood = models.CharField('Bairro', max_length=100, null=True, blank=True)
    number = models.CharField('Número', max_length=20, null=True, blank=True)
    complement = models.CharField('Complemento', max_length=100, null=True, blank=True)
    city = models.CharField('Cidade', max_length=100, null=True, blank=True)
    state = models.CharField('Estado', max_length=100, null=True, blank=True)
    country = models.CharField('País', max_length=100, null=True, blank=True)
    zip_code = models.CharField('CEP', max_length=20, null=True, blank=True)
    date_birth = models.DateTimeField('Data de nascimento', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_supplier_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_supplier_user_updated', verbose_name="Atualizado por")

    class Meta:
        verbose_name = 'Fornecedores Cliente'
        db_table = 'customer_suppliers'

    def __str__(self):
        return self.name
