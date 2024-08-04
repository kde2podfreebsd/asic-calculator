import os
from string import Template
import pdfkit

basedir = os.path.dirname(os.path.abspath(__file__))


def generate_pdf(chatid):
    template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uminers Proposal</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }
        .container {
            width: 80%;
            max-width: 900px;
            margin: 20px auto;
            background-color: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: right;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .header p {
            margin: 0;
            font-size: 14px;
        }
        .main-content {
            margin-top: 30px;
        }
        .main-content h2 {
            font-size: 18px;
            margin-bottom: 10px;
        }
        .main-content table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .main-content table, .main-content th, .main-content td {
            border: 1px solid #ddd;
        }
        .main-content th, .main-content td {
            padding: 10px;
            text-align: center;
        }
        .highlight {
            background-color: #f0f0f0;
        }
        .profit-calculation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .profit-calculation div {
            width: 48%;
        }
        .profit-calculation .chart {
            background-color: #f9f9f9;
            padding: 20px;
            text-align: center;
            border: 1px solid #ddd;
        }
        .profit-calculation .details {
            background-color: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
        }
        .profit-calculation .details table {
            width: 100%;
            border-collapse: collapse;
        }
        .profit-calculation .details th, .profit-calculation .details td {
            padding: 8px;
            text-align: left;
        }
        .footer {
            text-align: center;
            font-size: 12px;
            color: #888;
            margin-top: 20px;
        }
        .footer p {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Индивидуальное предложение</h1>
            <p>для $username $usersecondname</p>
        </div>
        <div class="main-content">
            <h2>Модель: Antminer S21 Pro (234Th)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Алгоритм</th>
                        <th>Хешрейт</th>
                        <th>Мощность</th>
                        <th>Цена/шт</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>SHA-256</td>
                        <td>234 TH/s</td>
                        <td>3 531 W</td>
                        <td>4 520 USDT</td>
                    </tr>
                </tbody>
            </table>
            <div class="profit-calculation">
                <div class="chart">
                    <p>Доход от инвестиций по монете BTC (Bitcoin)*</p>
                    <div>
                        <svg width="100" height="100">
                            <!-- Example pie chart, should be replaced with actual chart library or SVG -->
                            <circle cx="50" cy="50" r="45" fill="#f9f9f9" stroke="#ddd" stroke-width="10"/>
                            <circle cx="50" cy="50" r="45" fill="transparent" stroke="#00aaff" stroke-width="10" stroke-dasharray="101, 190" transform="rotate(-90, 50, 50)"/>
                        </svg>
                    </div>
                    <p>35.35% прибыль, 64.65% затраты на электроэнергию</p>
                </div>
                <div class="details">
                    <table>
                        <thead>
                            <tr>
                                <th></th>
                                <th>в день</th>
                                <th>в месяц</th>
                                <th>в год</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>доход</td>
                                <td>$12.02</td>
                                <td>$360.68</td>
                                <td>$4,388.23</td>
                            </tr>
                            <tr>
                                <td>затраты</td>
                                <td>$4.248</td>
                                <td>$127.44</td>
                                <td>$1,550.52</td>
                            </tr>
                            <tr class="highlight">
                                <td>прибыль</td>
                                <td>$7.77</td>
                                <td>$233.24</td>
                                <td>$2,837.71</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="payback-period">
                <h2>Расчет срока окупаемости инвестиций***</h2>
                <p>4520$ / 233.24$ = <strong>20 месяцев</strong></p>
                <p>* Актуальный курс BTC - 64 076. USD</p>
                <p>** Тариф на электроэнергию - 0.05 $ за kВт*ч</p>
                <p>*** Расчет срока окупаемости инвестиций произведен за 1 единицу оборудования. Обратите внимание, что расчеты основаны на средних значениях, поэтому ваши конечные результаты могут отличаться.</p>
            </div>
        </div>
        <div class="footer">
            <p>UMINERS TECHNOLOGY PTE. LTD.</p>
            <p>номер телефона: 8 (800) 4444-852</p>
            <p>email: sales@uminers.com</p>
            <p>telegram: @uminers</p>
            <p>01.08.2024</p>
        </div>
    </div>
</body>
</html>

    """

    t = Template(template)
    context = {
        "username": "Lol",
        "usersecondname": "Kekovich"
    }

    rendered_html = t.safe_substitute(context)

    with open(f'static/{chatid}.html', 'w') as f:
        f.write(rendered_html)

    pdfkit.from_string(rendered_html, f'static/{chatid}.pdf')


generate_pdf(123)