import helpers

from typing import Any
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path

STATICFILES_VENDOR_DIR = getattr(settings, "STATICFILES_VENDOR_DIR", None)

VENDOR_STATICFILES = {
    "flowbite.min.css": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js",
    "flowbite.min.js.map": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js.map",
}

class Command(BaseCommand):
    help = "Downloads vendor static files from specified URLs."

    def handle(self, *args: Any, **kwargs: Any) -> None:
        if not STATICFILES_VENDOR_DIR:
            self.stdout.write(self.style.ERROR("STATICFILES_VENDOR_DIR is not configured."))
            return

        vendor_dir = Path(STATICFILES_VENDOR_DIR)
        vendor_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write("Downloading vendor static files...\n")

        failed_downloads = []

        for filename, url in VENDOR_STATICFILES.items():
            destination_path = vendor_dir / filename

            try:
                success = helpers.download_to_local(url, destination_path)
                if success:
                    self.stdout.write(f"✓ Downloaded {filename} -> {destination_path}")
                else:
                    failed_downloads.append((filename, url))
                    self.stdout.write(self.style.ERROR(f"✗ Failed to download {filename} from {url}"))
            except Exception as e:
                failed_downloads.append((filename, url))
                self.stdout.write(self.style.ERROR(f"✗ Error downloading {filename}: {e}"))

        if not failed_downloads:
            self.stdout.write(self.style.SUCCESS("\nAll vendor static files downloaded successfully."))
        else:
            self.stdout.write(self.style.WARNING("\nSome vendor static files failed to download:"))
            for filename, url in failed_downloads:
                self.stdout.write(f" - {filename} from {url}")