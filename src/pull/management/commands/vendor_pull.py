import helpers

from typing import Any
from django.conf import settings
from django.core.management.base import BaseCommand

STATICFILES_VENDOR_DIR = getattr(settings, "STATICFILES_VENDOR_DIR", None)

VENDOR_STATICFILES = {
    "flowbite.min.css": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js",
    "flowbite.min.js.map": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js.map"
}

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write("Downloading vendor static files...")
        completed_urls = []

        for filename, url in VENDOR_STATICFILES.items():
            path = STATICFILES_VENDOR_DIR / filename
            dl_success = helpers.download_to_local(url, path)
            if dl_success:
                completed_urls.append(url)
                self.stdout.write(f"Downloaded {filename} to {path}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to download {filename} from {url}")
                )

        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write("All vendor static files downloaded successfully")
        else:
            self.stdout.write("Failed to download all vendor static files")