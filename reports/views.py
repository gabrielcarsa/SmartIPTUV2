from django.http import JsonResponse
from django.views.generic.base import TemplateView
from django.views import View
import requests
import datetime
from bs4 import BeautifulSoup

from debits.models import Enterprise

class PortfolioYearsDataView(View):

    def get(self, request):
        login_url = "https://ambiente.ibsystemlote.com.br/"
        session = requests.Session()

        payload = {
            "username": "gabrielcarsa@hotmail.com",
            "password": "123Mudar#"
        }

        login_response = session.post(login_url, data=payload, timeout=15)
        if login_response.status_code != 200:
            return JsonResponse({"error": "Erro ao fazer login."}, status=400)

        current_date = datetime.date.today()
        current_year = current_date.year
        results = {}

        enterprises = Enterprise.objects.all()
        enterprise_list = [
            {"name": e.name, "code_erp": e.code_erp} for e in enterprises
        ]

        if enterprises.exists():

            for i in range(5):
                current_year_loop = current_year + i
                inicio = current_date.strftime("%Y-%m-%d") if i == 0 else f"{current_year_loop}-01-01"
                fim = f"{current_year_loop}-12-31"
                results[current_year_loop] = {}

                for enterprise in enterprises:
                    report_url = (
                        f"https://ambiente.ibsystemlote.com.br/contratolocacao/recebimentos.php?"
                        f"inicio={inicio}&fim={fim}&cliente_idcliente=Todos&empreendimento_id={enterprise.code_erp}&"
                        "numero_lancamento=&numero_baixa=&situacao=1&tipo_periodo=2&idquadra=0&idlote=&excel=&"
                        "ordenar=quadra_lote&baixa_automatica=&contacorrente_id=Todos&mes=&investidor_cli=&"
                        "socio=&tipo_parcela=Parcela%20Financiamento"
                    )

                    report_form_response = session.get(report_url, timeout=15)
                    if report_form_response.status_code != 200:
                        results[current_year_loop][enterprise.code_erp] = None
                        continue

                    soup_result = BeautifulSoup(report_form_response.text, "html.parser")
                    rows = soup_result.find_all("tr")

                    if rows:
                        last_row = rows[-1]
                        tds = last_row.find_all("td")
                        if len(tds) >= 7:
                            total_amount = tds[6].get_text(strip=True)
                            results[current_year_loop][enterprise.code_erp] = total_amount
                        else:
                            results[current_year_loop][enterprise.code_erp] = None
                    else:
                        results[current_year_loop][enterprise.code_erp] = None

            return JsonResponse({"results": results, "enterprises": enterprise_list})
    
class PortfolioYearsTemplateView(TemplateView):
    template_name = "portfolio_years/list.html"