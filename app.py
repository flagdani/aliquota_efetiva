import logging
from flask import Flask, render_template, request

app = Flask(__name__)

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Calculator:
    def __init__(self):
        # Define as tabelas para os diferentes anexos
        self.tabelas = {
            'anexo_1': [
                (180000.00, 0.04, 0.00, 1),
                (360000.00, 0.073, 5940.00, 2),
                (720000.00, 0.095, 13860.00, 3),
                (1800000.00, 0.107, 22500.00, 4),
                (3600000.00, 0.143, 87300.00, 5),
                (4800000.00, 0.19, 378000.00, 6),
            ],
            'anexo_2': [
                (180000.00, 0.045, 0.00, 1),
                (360000.00, 0.078, 5940.00, 2),
                (720000.00, 0.10, 13860.00, 3),
                (1800000.00, 0.112, 22500.00, 4),
                (3600000.00, 0.147, 85500.00, 5),
                (4800000.00, 0.30, 720000.00, 6),
            ],
            'anexo_3': [
                (180000.00, 0.06, 0.00, 1),
                (360000.00, 0.112, 9360.00, 2),
                (720000.00, 0.135, 17640.00, 3),
                (1800000.00, 0.16, 35640.00, 4),
                (3600000.00, 0.21, 125640.00, 5),
                (4800000.00, 0.33, 648000.00, 6),
            ],
            'anexo_4': [
                (180000.00, 0.045, 0.00, 1),
                (360000.00, 0.09, 8100.00, 2),
                (720000.00, 0.102, 12420.00, 3),
                (1800000.00, 0.14, 39780.00, 4),
                (3600000.00, 0.22, 183780.00, 5),
                (4800000.00, 0.33, 828000.00, 6),
            ],
            'anexo_5': [
                (180000.00, 0.155, 0.00, 1),
                (360000.00, 0.18, 4500.00, 2),
                (720000.00, 0.195, 9900.00, 3),
                (1800000.00, 0.205, 17100.00, 4),
                (3600000.00, 0.23, 62100.00, 5),
                (4800000.00, 0.305, 540000.00, 6),
            ]
        }

        self.iss_percentuais = {
            'anexo_3': {
                1: 0.335,
                2: 0.320,
                3: 0.325,
                4: 0.325,
                5: 0.335,
                6: 0.150
            },
            'anexo_4': {
                1: 0.445,
                2: 0.40,
                3: 0.40,
                4: 0.40,
                5: 0.40,
                6: 0.0
            },
            'anexo_5': {
                1: 0.140,
                2: 0.170,
                3: 0.190,
                4: 0.210,
                5: 0.235,
                6: 0.155
            }
        }

        self.icms_tabela = {
            'anexo_1': {
                1: 0.34,
                2: 0.34,
                3: 0.335,
                4: 0.335,
                5: 0.335,
                6: 0.0
            },
            'anexo_2': {
                1: 0.32,
                2: 0.32,
                3: 0.32,
                4: 0.32,
                5: 0.32,
                6: 0.0
            }
        }

    def calcular_aliquota_efetiva(self, rbt12, anexo):
        faixas = self.tabelas.get(anexo)
        if not faixas:
            logging.error(f"Anexo {anexo} não reconhecido.")
            return None, None

        faixa_num = None
        aliquota_efetiva = None

        for faixa in faixas:
            limite_superior, aliquota, deducao, faixa_num = faixa
            if rbt12 <= limite_superior:
                aliquota_efetiva = ((rbt12 * aliquota) - deducao) / rbt12

                # Ajuste para ANEXO IV
                if anexo == 'anexo_4' and aliquota_efetiva < 0.045:
                    logging.info(
                        f"Alíquota efetiva calculada para ANEXO IV ({aliquota_efetiva:.4f}) é menor que o mínimo de 4,5%. Ajustando para 4,5%.")
                    aliquota_efetiva = 0.045  # 4,5%

                return round(aliquota_efetiva, 4), faixa_num

        # Se RBT12 excede todas as faixas, utiliza a última faixa
        ultima_faixa = faixas[-1]
        limite_superior, aliquota, deducao, faixa_num = ultima_faixa
        aliquota_efetiva = ((rbt12 * aliquota) - deducao) / rbt12

        # Ajuste para ANEXO IV
        if anexo == 'anexo_4' and aliquota_efetiva < 0.045:
            logging.info(
                f"Alíquota efetiva calculada para ANEXO IV ({aliquota_efetiva:.4f}) é menor que o mínimo de 4,5%. Ajustando para 4,5%.")
            aliquota_efetiva = 0.045  # 4,5%

        return round(aliquota_efetiva, 4), faixa_num

    def calcular_imposto(self, aliquota, faixa, anexo):
        # Verifica se o anexo é I ou II para calcular ICMS
        if anexo in ['anexo_1', 'anexo_2']:
            icms_percent = self.icms_tabela.get(anexo, {}).get(faixa, 0)
            imposto = aliquota * icms_percent
            return round(imposto, 4), 'ICMS'
        else:
            # ISS para os demais anexos
            iss_percent = self.iss_percentuais.get(anexo, {}).get(faixa, 0)
            imposto = aliquota * iss_percent
            imposto_nome = 'ISS'

            # Aplicar a limitação de ISS
            if imposto_nome == 'ISS':
                if imposto > 0.05:
                    logging.info(f"ISS original de {imposto:.4f} excede 5%. Ajustando para 5%.")
                    imposto = 0.05
                elif imposto < 0.02:
                    logging.info(f"ISS original de {imposto:.4f} é inferior a 2%. Ajustando para 2%.")
                    imposto = 0.02

            return round(imposto, 4), imposto_nome


calculator = Calculator()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Remover símbolo de moeda e formatar corretamente
            rbt12_str = request.form.get('rbt12').replace('R$', '').replace('.', '').replace(',', '.').strip()
            rpa_str = request.form.get('rpa').replace('R$', '').replace('.', '').replace(',', '.').strip()

            rbt12 = float(rbt12_str)
            rpa = float(rpa_str)
            anexo = request.form.get('anexo')

            if anexo not in ['anexo_1', 'anexo_2', 'anexo_3', 'anexo_4', 'anexo_5']:
                return render_template('index.html', error="Anexo inválido selecionado.",
                                       rbt12=request.form.get('rbt12'), rpa=request.form.get('rpa'))

            aliquota, faixa = calculator.calcular_aliquota_efetiva(rbt12, anexo)
            if aliquota is None:
                return render_template('index.html', error="Erro no cálculo da alíquota.",
                                       rbt12=request.form.get('rbt12'), rpa=request.form.get('rpa'))

            imposto, imposto_nome = calculator.calcular_imposto(aliquota, faixa, anexo)

            resultado = {
                'Anexo': anexo.upper().replace('_', ' ').replace('ANEXO ', 'ANEXO '),
                'Alíquota Efetiva': f"{aliquota * 100:.2f}%",
                'Imposto': f"{imposto * 100:.2f}% de {imposto_nome}"
            }

            return render_template('index.html', resultado=resultado)

        except ValueError:
            return render_template('index.html', error="Valores de RBT12 e RPA devem ser numéricos.",
                                   rbt12=request.form.get('rbt12'), rpa=request.form.get('rpa'))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
