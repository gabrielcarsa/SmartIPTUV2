from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return value / arg
    except (ZeroDivisionError, TypeError):
        return 0
    
@register.filter
def format_phone(value):
    t = ''.join(filter(str.isdigit, str(value)))
    if len(t) == 11:
        return f"({t[:2]}) {t[2:7]}-{t[7:]}"
    elif len(t) == 10:
        return f"({t[:2]}) {t[2:6]}-{t[6:]}"
    return value

@register.filter
def format_cpf(value):
    # Remove todos os caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, str(value)))
    
    # Verifica se o CPF tem exatamente 11 dígitos
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    # Caso tenha 10 dígitos (ex: CPF com 1 número faltando)
    elif len(cpf) == 10:
        return f"{cpf[:2]}.{cpf[2:5]}.{cpf[5:8]}-{cpf[8:]}"
    
    # Se não for nem 11 nem 10 dígitos, retorna o valor original
    return value


@register.filter
def format_cnpj(value):
    # Remove todos os caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, str(value)))
    
    # Verifica se o CNPJ tem exatamente 14 dígitos
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    
    # Caso tenha 13 dígitos (CNPJ com 1 número faltando)
    elif len(cnpj) == 13:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:11]}-{cnpj[11:]}"
    
    # Se não for nem 14 nem 13 dígitos, retorna o valor original
    return value