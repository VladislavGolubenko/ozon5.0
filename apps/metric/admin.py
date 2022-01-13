from django.contrib import admin
from .models import OzonMetrics


class OzonMetricsAdmin(admin.ModelAdmin):
    list_display = ("user_id", "product_id", "product_name", "hits_view_search", "hits_view_pdp", "hits_view",
                    "hits_tocart_search", "hits_tocart_pdp", "hits_tocart", "session_view_search", "session_view_pdp",
                    "session_view", "conv_tocart_search", "conv_tocart_pdp", "conv_tocart", "revenue", "returns",
                    "cancellations", "ordered_units", "delivered_units", "adv_view_pdp", "adv_view_search_category",
                    "adv_view_all", "adv_sum_all", "position_category", "postings", "postings_premium", "creating_date")


admin.site.register(OzonMetrics, OzonMetricsAdmin)

