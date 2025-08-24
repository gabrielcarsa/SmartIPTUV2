from django.views.generic.base import TemplateView
import requests
import datetime
from bs4 import BeautifulSoup

class PortfolioYearsFormView(TemplateView):
    template_name = "portfolio_years/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        login_url = "https://ambiente.ibsystemlote.com.br/"

        session = requests.Session()

        payload = {
            "username": "gabrielcarsa@hotmail.com",
            "password": "123Mudar#"
        }

        # 1. Login ERP
        login_response = session.post(login_url, data=payload)

        if login_response.status_code != 200:
            context["error_menssage"] = "Erro ao fazer login."
            return context
        
        current_date = datetime.date.today()
        current_year = current_date.year

        results_years = []
        results_amounts = []
        
        # 2. Access reports
        for i in range(23):
            
            current_year_loop = current_year + i

            if i == 0:
                inicio = current_date.strftime("%Y-%m-%d")
            else:
                inicio = f"{current_year_loop}-01-01"

            fim = f"{current_year_loop}-12-31"

            report_url = (
                f"https://ambiente.ibsystemlote.com.br/contratolocacao/recebimentos.php?"
                f"inicio={inicio}&fim={fim}&cliente_idcliente=Todos&empreendimento_id=1&"
                "numero_lancamento=&numero_baixa=&situacao=1&tipo_periodo=2&idquadra=0&idlote=&excel=&"
                "ordenar=quadra_lote&baixa_automatica=&contacorrente_id=Todos&mes=&investidor_cli=&"
                "socio=&tipo_parcela=Parcela%20Financiamento"
            )

            report_form_response = session.get(report_url)
                
            if report_form_response.status_code != 200:
                context["error_menssage"] = f"Erro ao acessar relatório do ano {current_year_loop}."
                return context
            
            # 3. Get the results
            soup_result = BeautifulSoup(report_form_response.text, "html.parser")
            rows = soup_result.find_all("tr")

            if rows:
                last_row = rows[-1]
                tds = last_row.find_all("td")

                if len(tds) >= 7:

                    total_amount = tds[6].get_text(strip=True)

                    results_years.append(current_year_loop)
                    results_amounts.append(total_amount)

                else:
                    context["error_menssage"] = "A linha não possui 7 colunas."
            else:
                context["error_menssage"] = "Nenhuma linha encontrada."

        results = list(zip(results_years, results_amounts))
        context["results"] = results        
        return context