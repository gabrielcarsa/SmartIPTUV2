from django.db import models
from django.contrib.auth.models import User

from customer_suppliers.models import CustomerSupplier

class Enterprise(models.Model):
    name = models.CharField("Nome", max_length=100)
    city = models.CharField("Cidade", max_length=100)
    state = models.CharField("Estado", max_length=100)
    property_registration = models.CharField("Matrícula", max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enterprise_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enterprise_user_updated', verbose_name="Atualizado por")

    class Meta:
        verbose_name = 'Empreendimento'
        db_table = 'enterprises'

    def __str__(self):
        return self.name
    
class Block(models.Model):
    name = models.CharField("Nome", max_length=100)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name="Empreendimento", related_name="blocks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_user_updated', verbose_name="Atualizado por")

    class Meta:
        verbose_name = 'Quadra'
        db_table = 'blocks'

    def __str__(self):
        return self.name
    
class Lot(models.Model):
    lot = models.CharField("Lote", max_length=100)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, verbose_name="Quadra", related_name="lots")
    square_meters = models.FloatField("Metros quadrados")
    value = models.DecimalField("Valor do lote", max_digits=10, decimal_places=2)
    address = models.CharField("Endereço", max_length=100)
    property_registration = models.CharField("Matrícula", max_length=30)
    municipal_registration = models.CharField("Inscrição municipal", max_length=30)
    front_footage = models.CharField("Metragem frente", max_length=100)
    bottom_footage = models.CharField("Metragem fundo", max_length=100)
    right_footage = models.CharField("Metragem direita", max_length=100)
    left_footage = models.CharField("Metragem esquerda", max_length=100)
    corner_footage = models.CharField("Metragem esquina", max_length=100)
    front_confrontation = models.CharField("Confrontação frente", max_length=100)
    bottom_confrontation = models.CharField("Confrontação fundo", max_length=100)
    right_confrontation = models.CharField("Confrontação direita", max_length=100)
    left_confrontation = models.CharField("Confrontação esquerda", max_length=100)
    is_property_deed = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lot_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lot_user_updated', verbose_name="Atualizado por")

    class Meta:
        verbose_name = 'Lote'
        db_table = 'lots'

    def __str__(self):
        return self.lot
    
class SalesContract(models.Model):
    contract_date = models.DateField("Data do contrato")
    customer_supplier = models.ForeignKey(CustomerSupplier, verbose_name="Cliente", on_delete=models.CASCADE, related_name="contracts")
    start_date = models.DateField("Data inicial das parcelas", null=True, blank=True)
    number_of_installment = models.IntegerField("Número de parcelas", null=True, blank=True)
    installment_value = models.DecimalField("Valor das parcelas", max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_contract_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_contract_user_updated', verbose_name="Atualizado por")
