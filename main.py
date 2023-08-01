from flask import Flask, render_template, request
from jinja2 import Environment


app = Flask(__name__)
env = Environment()

@app.route('/', methods=['GET', 'POST'])
def salaries():

    months = ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień',
              'październik', 'listopad', 'grudzień']

    months_dict = {}
    n = 0
    for month in months:
        months_dict[n] = {'month': month, 'brutto': '', 'ub_emerytalne': '', 'ub_rentowe': '', 'ub_chorobowe': '',
                              'ub_zdrowotne': '', 'podst_opodatkowania': '', 'zaliczka_na_PIT': '', 'netto': ''}
        n += 1

    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        salary_input = request.form.get('salaryInput').replace(',', '.')
        work_at_residence = request.form.get('workAtResidence')

        if salary_input is not None and salary_input.strip() != "":
            try:
                gross_salary = float(salary_input)
                cost_of_revenue = 250 if work_at_residence == 'on' else 300
                first_tax_rate = 0.12
                second_tax_rate = 0.32

                # Thresholds
                tax_threshold = 120000
                ss_threshold = 208050

                salary_total = 0
                tax_base_total = 0

                for month in range(12):
                    salary_total += gross_salary

                    # Check if social securities threshold has been exceeded in a month
                    if salary_total > ss_threshold:
                        ub_emerytalne = 0 if ss_threshold - salary_total + gross_salary < 0 else \
                            round((ss_threshold - salary_total + gross_salary) * 0.0976, 2)
                        ub_rentowe = 0 if ss_threshold - salary_total + gross_salary < 0 else \
                            round((ss_threshold - salary_total + gross_salary) * 0.015, 2)
                    else:
                        ub_emerytalne = round(gross_salary * 0.0976, 2)
                        ub_rentowe = round(gross_salary * 0.015, 2)
                    ub_chorobowe = round(gross_salary * 0.0245, 2)
                    ub_zdrowotne = round((gross_salary - ub_emerytalne - ub_rentowe - ub_chorobowe) * 0.09, 2)
                    podst_opodatkowania = round(gross_salary - ub_emerytalne - ub_rentowe - ub_chorobowe -
                                                cost_of_revenue, 0)
                    tax_base_total += podst_opodatkowania
                    kwota_wolna = 30000 * 0.12 / 12

                    # Check if tax threshold has been exceeded in a month
                    if tax_base_total > tax_threshold:
                        first_tax_threshold = \
                            0 if tax_threshold - tax_base_total + podst_opodatkowania < 0 \
                                else tax_threshold - tax_base_total + podst_opodatkowania
                        second_tax_threshold = \
                            0 if gross_salary - first_tax_threshold < 0 else podst_opodatkowania - first_tax_threshold

                        zaliczka_na_PIT = round(first_tax_threshold * first_tax_rate +
                                                second_tax_threshold * second_tax_rate - kwota_wolna, 0)
                    else:
                        zaliczka_na_PIT = 0 if round(podst_opodatkowania * first_tax_rate - kwota_wolna, 0) < 0 \
                            else round(podst_opodatkowania * first_tax_rate - kwota_wolna, 0)
                    netto = round(gross_salary - ub_emerytalne - ub_rentowe - ub_chorobowe - ub_zdrowotne - zaliczka_na_PIT,
                                  2)
                    months_dict[month]['brutto'] = '{:,.2f}'.format(gross_salary).replace(',', ' ')
                    months_dict[month]['ub_emerytalne'] = '{:,.2f}'.format(ub_emerytalne).replace(',', ' ')
                    months_dict[month]['ub_rentowe'] = '{:,.2f}'.format(ub_rentowe).replace(',', ' ')
                    months_dict[month]['ub_chorobowe'] = '{:,.2f}'.format(ub_chorobowe).replace(',', ' ')
                    months_dict[month]['ub_zdrowotne'] = '{:,.2f}'.format(ub_zdrowotne).replace(',', ' ')
                    months_dict[month]['podst_opodatkowania'] = '{:,.2f}'.format(podst_opodatkowania).replace(',', ' ')
                    months_dict[month]['zaliczka_na_PIT'] = '{:,.2f}'.format(zaliczka_na_PIT).replace(',', ' ')
                    months_dict[month]['netto'] = '{:,.2f}'.format(netto).replace(',', ' ')

                # Add total values to dictionary
                total_values = {
                    'brutto': 0,
                    'ub_emerytalne': 0,
                    'ub_rentowe': 0,
                    'ub_chorobowe': 0,
                    'ub_zdrowotne': 0,
                    'podst_opodatkowania': 0,
                    'zaliczka_na_PIT': 0,
                    'netto': 0
                }

                for month_data in months_dict.values():
                    for key in total_values:
                        total_values[key] += float(month_data[key].replace(',', '').replace(' ', ''))

                for key in total_values:
                    total_values[key] = '{:,.2f}'.format(total_values[key]).replace(',', ' ')

                # Add the 'sum' key to the months_dict dictionary
                months_dict['suma'] = total_values

                return render_template('salary_table.html', months_dict=months_dict, work_at_residence=work_at_residence)
            except ValueError:
                return render_template('index.html', error_message="Wprowadź prawidłową kwotę brutto.")
        else:
            return render_template('index.html', error_message="Wprowadź kwotę brutto.")


if __name__ == '__main__':
    app.run(debug=True)
