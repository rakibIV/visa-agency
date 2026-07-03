from django.core.management.base import BaseCommand

from applicant.currency import sync_currency_rates
from country.models import Country
from visa.models import VisaJob
from applicant.models import ApplicantPayment


class Command(BaseCommand):
    help = "Refresh and store currency exchange rates in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--target",
            default="EUR",
            help="Target currency code. Default: EUR",
        )
        parser.add_argument(
            "--currency",
            action="append",
            dest="currencies",
            help="Currency code to refresh. Can be provided multiple times.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Refresh even if a cached rate is still fresh.",
        )

    def handle(self, *args, **options):
        target_currency = options["target"]
        currencies = options["currencies"]
        force = options["force"]

        if not currencies:
            currencies = sorted(
                {
                    code.upper()
                    for code in (
                        list(Country.objects.values_list("currency", flat=True))
                        + list(VisaJob.objects.values_list("currency", flat=True))
                        + list(ApplicantPayment.objects.values_list("currency", flat=True))
                    )
                    if code
                }
            )

        if not currencies:
            self.stdout.write(
                self.style.WARNING("No currencies found to refresh.")
            )
            return

        rates = sync_currency_rates(
            currencies=currencies,
            to_currency=target_currency,
            force=force,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {len(rates)} currency rate(s) to {target_currency}."
            )
        )

        for rate in rates:
            self.stdout.write(
                f"{rate.base_currency}/{rate.target_currency} = {rate.rate} "
                f"(fetched {rate.fetched_at:%Y-%m-%d %H:%M:%S%z})"
            )
