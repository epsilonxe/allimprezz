from datetime import timedelta

from django.conf import settings
from django.db import models

from libs.tours.cost import CostItem as CostItemLib


class Tour(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    destination = models.CharField(max_length=255)
    duration_days = models.PositiveIntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tours_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date and self.end_date:
            self.duration_days = (self.end_date - self.start_date).days + 1
        elif self.start_date and self.duration_days:
            self.end_date = self.start_date + timedelta(days=self.duration_days - 1)
        elif self.end_date and self.duration_days:
            self.start_date = self.end_date - timedelta(days=self.duration_days - 1)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TourCostScenario(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='cost_scenarios')
    label = models.CharField(max_length=255, blank=True, default='')
    num_pax = models.PositiveIntegerField()
    num_tour_leaders = models.PositiveIntegerField(default=0)
    markup_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    selling_price_per_pax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default='')
    is_desired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.tour.name} - {self.num_pax} pax"


class TourCostItem(models.Model):
    CATEGORY_CHOICES = [
        (cat, cat.replace('_', ' ').title())
        for cat in CostItemLib.CATEGORY_CHOICES
    ]

    scenario = models.ForeignKey(TourCostScenario, on_delete=models.CASCADE, related_name='items')
    item_number = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    pay_to = models.CharField(max_length=255, blank=True, default='')
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='THB')
    is_synced = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['item_number']

    def __str__(self):
        return self.name


class TourExchangeRate(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='exchange_rates')
    currency_code = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        unique_together = ['tour', 'currency_code']

    def __str__(self):
        return f"{self.currency_code} = {self.rate}"
