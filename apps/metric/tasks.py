import requests
from datetime import datetime
from datetime import timedelta

from .models import OzonMetrics
from ..account.models import User
from ozon.celery import app


@app.task(bind=True, name="get_analitic_data")
def get_analitic_data(*args, **kwargs):
    user_id = kwargs.get('user_id')


    user_data = User.objects.get(id=user_id)
    ozon_ovner = str(user_data.ozon_id)

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    if day < 10:
        date_from = f"{year}-{month}-0{day}T00:00:00Z"
        date_to = f"{year}-{month}-0{day}T23:55:00Z"
    else:
        date_from = f"{year}-{month}-{day}T00:00:00Z"
        date_to = f"{year}-{month}-{day}T23:55:00Z"

    request_post = requests.post('https://api-seller.ozon.ru/v1/analytics/data',
                                 json={
                                        "date_from": date_from,
                                        "date_to": date_to,
                                        "dimension": [
                                            "sku"
                                        ],
                                        "limit": 1000,
                                        "metrics": [
                                            "hits_view_search",
                                            "hits_view_pdp",
                                            "hits_view",
                                            "hits_tocart_search",
                                            "hits_tocart_pdp",
                                            "hits_tocart",
                                            "session_view_search",
                                            "session_view_pdp",
                                            "session_view",
                                            "conv_tocart_search",
                                            "conv_tocart_pdp",
                                            "conv_tocart",
                                            "revenue",
                                            "returns",
                                            "cancellations",
                                            "ordered_units",
                                            "delivered_units",
                                            "adv_view_pdp",
                                            "adv_view_search_category",
                                            "adv_view_all",
                                            "adv_sum_all",
                                            "position_category",
                                            "postings",
                                            "postings_premium"
                                        ],
                                        "offset": 0,
                                        "sort": [
                                            {
                                                "key": "hits_view",
                                                "order": "ASC"
                                            }
                                        ]
                                    },
                                 headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()
    result = request_json['result']
    datas = result['data']

    for data in datas:
        dimensions = data['dimensions']

        for dimension in dimensions:
            product_id = dimension['id']
            product_name = dimension['name']

        metrics = data['metrics']
        hits_view_search = metrics[0]
        hits_view_pdp = metrics[1]
        hits_view = metrics[2]
        hits_tocart_search = metrics[3]
        hits_tocart_pdp = metrics[4]
        hits_tocart = metrics[5]
        session_view_search = metrics[6]
        session_view_pdp = metrics[7]
        session_view = metrics[8]
        conv_tocart_search = metrics[9]
        conv_tocart_pdp = metrics[10]
        conv_tocart = metrics[11]
        revenue = metrics[12]
        returns = metrics[13]
        cancellations = metrics[14]
        ordered_units = metrics[15]
        delivered_units = metrics[16]
        adv_view_pdp = metrics[17]
        adv_view_search_category = metrics[18]
        adv_view_all = metrics[19]
        adv_sum_all = metrics[20]
        position_category = metrics[21]
        postings = metrics[22]
        postings_premium = metrics[23]

        OzonMetrics.objects.create_ozon_metrics(user_id=user_data, product_id=product_id, product_name=product_name,
                                                hits_view_search=hits_view_search, hits_view_pdp=hits_view_pdp,
                                                hits_view=hits_view, hits_tocart_search=hits_tocart_search,
                                                hits_tocart_pdp=hits_tocart_pdp, hits_tocart=hits_tocart,
                                                session_view_search=session_view_search,
                                                session_view_pdp=session_view_pdp, session_view=session_view,
                                                conv_tocart_search=conv_tocart_search, conv_tocart_pdp=conv_tocart_pdp,
                                                conv_tocart=conv_tocart, revenue=revenue, returns=returns,
                                                cancellations=cancellations, ordered_units=ordered_units,
                                                delivered_units=delivered_units, adv_view_pdp=adv_view_pdp,
                                                adv_view_search_category=adv_view_search_category,
                                                adv_view_all=adv_view_all,
                                                adv_sum_all=adv_sum_all, position_category=position_category,
                                                postings=postings,
                                                postings_premium=postings_premium)


@app.task(bind=True, name="update_analitics_data")
def update_analitics_data(*args, **kwargs):

    user_id = kwargs.get('user_id')
    date = kwargs.get('today')

    user_data = User.objects.get(id=user_id)
    ozon_ovner = str(user_data.ozon_id)

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    if day < 10:
        date_from = f"{year}-{month}-0{day}T00:00:00Z"
        date_to = f"{year}-{month}-0{day}T23:55:00Z"
    else:
        date_from = f"{year}-{month}-{day}T00:00:00Z"
        date_to = f"{year}-{month}-{day}T23:55:00Z"

    request_post = requests.post('https://api-seller.ozon.ru/v1/analytics/data',
                                 json={
                                     "date_from": date_from,
                                     "date_to": date_to,
                                     "dimension": [
                                         "sku"
                                     ],
                                     "limit": 1000,
                                     "metrics": [
                                         "hits_view_search",
                                         "hits_view_pdp",
                                         "hits_view",
                                         "hits_tocart_search",
                                         "hits_tocart_pdp",
                                         "hits_tocart",
                                         "session_view_search",
                                         "session_view_pdp",
                                         "session_view",
                                         "conv_tocart_search",
                                         "conv_tocart_pdp",
                                         "conv_tocart",
                                         "revenue",
                                         "returns",
                                         "cancellations",
                                         "ordered_units",
                                         "delivered_units",
                                         "adv_view_pdp",
                                         "adv_view_search_category",
                                         "adv_view_all",
                                         "adv_sum_all",
                                         "position_category",
                                         "postings",
                                         "postings_premium"
                                     ],
                                     "offset": 0,
                                     "sort": [
                                         {
                                             "key": "hits_view",
                                             "order": "ASC"
                                         }
                                     ]
                                 },
                                 headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()
    result = request_json['result']
    datas = result['data']

    for data in datas:
        dimensions = data['dimensions']

        for dimension in dimensions:
            product_id = dimension['id']
            product_name = dimension['name']

        metrics = data['metrics']
        hits_view_search = metrics[0]
        hits_view_pdp = metrics[1]
        hits_view = metrics[2]
        hits_tocart_search = metrics[3]
        hits_tocart_pdp = metrics[4]
        hits_tocart = metrics[5]
        session_view_search = metrics[6]
        session_view_pdp = metrics[7]
        session_view = metrics[8]
        conv_tocart_search = metrics[9]
        conv_tocart_pdp = metrics[10]
        conv_tocart = metrics[11]
        revenue = metrics[12]
        returns = metrics[13]
        cancellations = metrics[14]
        ordered_units = metrics[15]
        delivered_units = metrics[16]
        adv_view_pdp = metrics[17]
        adv_view_search_category = metrics[18]
        adv_view_all = metrics[19]
        adv_sum_all = metrics[20]
        position_category = metrics[21]
        postings = metrics[22]
        postings_premium = metrics[23]

        if date is not None:
            date = datetime.now().date()
            metrics_to_update = OzonMetrics.objects.filter(product_id=product_id, creating_date=date)
        else:
            date = datetime.now().date() - timedelta(1)
            metrics_to_update = OzonMetrics.objects.filter(product_id=product_id, creating_date=date)

        metrics_to_update.update(user_id=user_data, product_id=product_id, product_name=product_name,
                                 hits_view_search=hits_view_search, hits_view_pdp=hits_view_pdp, hits_view=hits_view,
                                 hits_tocart_search=hits_tocart_search, hits_tocart_pdp=hits_tocart_pdp,
                                 hits_tocart=hits_tocart, session_view_search=session_view_search,
                                 session_view_pdp=session_view_pdp, session_view=session_view,
                                 conv_tocart_search=conv_tocart_search, conv_tocart_pdp=conv_tocart_pdp,
                                 conv_tocart=conv_tocart, revenue=revenue, returns=returns, cancellations=cancellations,
                                 ordered_units=ordered_units, delivered_units=delivered_units, adv_view_pdp=adv_view_pdp,
                                 adv_view_search_category=adv_view_search_category, adv_view_all=adv_view_all,
                                 adv_sum_all=adv_sum_all, position_category=position_category, postings=postings,
                                 postings_premium=postings_premium)