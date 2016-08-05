from ecs import bootstrap
from ecs.billing.models import Price
from ecs.billing.models import STUDY_PRICING_OTHER, STUDY_PRICING_MULTICENTRIC_AMG_MAIN, STUDY_PRICING_MULTICENTRIC_AMG_LOCAL, STUDY_PRICING_REMISSION, EXTERNAL_REVIEW_PRICING


@bootstrap.register()
def prices():
    prices = {
        STUDY_PRICING_OTHER: 1800,
        STUDY_PRICING_MULTICENTRIC_AMG_MAIN: 4500,
        STUDY_PRICING_MULTICENTRIC_AMG_LOCAL: 600,
        STUDY_PRICING_REMISSION: 0,
        EXTERNAL_REVIEW_PRICING: 200,
    }
    for category, price in prices.items():
        Price.objects.update_or_create(category=category, defaults={
            'price': price,
        })
