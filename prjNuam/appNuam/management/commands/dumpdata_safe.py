import sys

from django.apps import apps
from django.core.management import BaseCommand, call_command
from django.db import connections


class Command(BaseCommand):
    help = "Dump data solo de tablas existentes, omitiendo modelos sin tabla."

    def add_arguments(self, parser):
        parser.add_argument(
            "--indent",
            type=int,
            default=4,
            help="Número de espacios para indentar el JSON (default: 4).",
        )
        parser.add_argument(
            "--natural-foreign",
            action="store_true",
            default=True,
            help="Usar claves naturales para FKs (se mantiene como true).",
        )
        parser.add_argument(
            "--natural-primary",
            action="store_true",
            default=True,
            help="Usar claves naturales para PKs (se mantiene como true).",
        )

    def handle(self, *args, **options):
        connection = connections["default"]
        existing_tables = set(connection.introspection.table_names())

        model_labels = []
        for model in apps.get_models():
            meta = model._meta
            # Saltar proxies
            if meta.proxy:
                continue
            # Saltar modelos sin tabla o sin gestionar cuya tabla no existe
            if meta.db_table not in existing_tables:
                continue
            if meta.managed is False and meta.db_table not in existing_tables:
                continue
            model_labels.append(f"{meta.app_label}.{meta.model_name}")

        if not model_labels:
            self.stdout.write(self.style.WARNING("No se encontraron tablas existentes para exportar."))
            return

        self.stdout.write(self.style.NOTICE(f"Exportando {len(model_labels)} modelos con tabla presente..."))

        call_command(
            "dumpdata",
            *model_labels,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            indent=options["indent"],
            stdout=sys.stdout,
        )
