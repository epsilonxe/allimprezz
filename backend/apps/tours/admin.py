from django.contrib import admin

from .models import Tour, TourCostItem, TourCostScenario, TourExchangeRate


class TourCostItemInline(admin.TabularInline):
    model = TourCostItem
    extra = 0


class TourCostScenarioInline(admin.TabularInline):
    model = TourCostScenario
    extra = 0
    show_change_link = True


class TourExchangeRateInline(admin.TabularInline):
    model = TourExchangeRate
    extra = 0


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'duration_days', 'start_date', 'end_date', 'status', 'created_by']
    list_filter = ['status']
    search_fields = ['name', 'destination']
    inlines = [TourCostScenarioInline, TourExchangeRateInline]


@admin.register(TourCostScenario)
class TourCostScenarioAdmin(admin.ModelAdmin):
    list_display = ['tour', 'num_pax', 'markup_percent', 'selling_price_per_pax']
    inlines = [TourCostItemInline]
