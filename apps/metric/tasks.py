import requests
from datetime import datetime
from datetime import timedelta

from .models import OzonMetrics
from ..account.models import User
from ozon.celery import app

def get_each_analitic_data(api_key:str, marketplace_id:str, metrics:list)->list:
    date_from = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
    date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
    request_post = requests.post('https://api-seller.ozon.ru/v1/analytics/data',
                                    json={
                                            "date_from": date_from,
                                            "date_to": date_to,
                                            "dimension": [
                                                "sku"
                                            ],
                                            "limit": 1000,
                                            "metrics": metrics,
                                            "offset": 0,
                                            # "sort": [
                                            #     {
                                            #         "key": "hits_view",
                                            #         "order": "ASC"
                                            #     }
                                            # ]
                                        },
                                    headers={'Client-Id': marketplace_id, 'Api-Key': api_key,
                                            'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()
    #print(request_json)
    #print()
    #print()
    result = request_json.get('result')
    if result is not None:
        return result.get("data")
    else:
        return []


def collect_metrics(first_metric:list, second_metric:list) -> list:
    for f_metric in first_metric:
        for s_metric in second_metric:

            if f_metric.get("dimensions")[0].get("id") == s_metric.get("dimensions")[0].get("id"):
                f_metric["metrics"] += s_metric["metrics"]
    return first_metric


@app.task(bind=True, name="get_analitic_data")
def get_analitic_data(*args, **kwargs):
    user_id = kwargs.get('user_id')
    
    first_metrics = [
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
                    "revenue"
                ]
    
    last_metrics = [
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
                ]
    if user_id is None:
        user_data = User.objects.all()
    else:

        user_data = [User.objects.get(id=user_id)]
    
    for user in user_data:
        for marketplace in user.marketplace_data.all():
            print(marketplace)
            marketplace_id = str(marketplace.marketplace_id)
            api_key = str(marketplace.api_key)
            first_metric = get_each_analitic_data(api_key=api_key, marketplace_id=marketplace_id, metrics=first_metrics)
            second_metric = get_each_analitic_data(api_key=api_key, marketplace_id=marketplace_id, metrics=last_metrics)
            all_metrics = collect_metrics(first_metric, second_metric)
            for data in all_metrics:
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

                OzonMetrics.objects.create_ozon_metrics(user_id=user, product_id=product_id, product_name=product_name,
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
    user_id = kwargs.get("user_id")
    user_data = User.objects.get(id=user_id)
    
    date_from = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
    date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
    for marketplace in user_data.marketplace_data.all():
        print(marketplace)
        marketplace_id = str(marketplace.marketplace_id)
        api_key = str(marketplace.api_key)
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
                                    headers={'Client-Id': marketplace_id, 'Api-Key': api_key,
                                            'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        request_json = request_post.json()
        #print(request_json)
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