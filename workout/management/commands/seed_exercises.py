from django.core.management.base import BaseCommand
from workout.models import Exercise


EXERCISES = [
    {
        "order": 1,
        "name": "Quad Sets",
        "name_ml": "ക്വാഡ് സെറ്റ്സ്",
        "description": "Pressing the knee down into a rolled towel",
        "description_ml": "മുട്ടിനടിയിൽ തുണി വെച്ച് താഴേക്ക് അമർത്തുന്നത്",
    },
    {
        "order": 2,
        "name": "Heel Props",
        "name_ml": "ഹീൽ പ്രോപ്സ്",
        "description": "Keeping the leg straight with a rolled towel under the heel",
        "description_ml": "ഉപ്പൂറ്റിക്കടിയിൽ തുണി വെച്ച് കാൽ നിവർത്തി വെക്കുന്നത്",
    },
    {
        "order": 3,
        "name": "Short Arc Quads (SAQ)",
        "name_ml": "ഷോർട്ട് ആർക്ക് ക്വാഡ്സ്",
        "description": "Lifting only the foot with a supportive pillow under the knee",
        "description_ml": "മുട്ടിനടിയിൽ പില്ലോ വെച്ച് പാദം മാത്രം ഉയർത്തുന്നത്",
    },
    {
        "order": 4,
        "name": "Straight Leg Raise (SLR)",
        "name_ml": "സ്ട്രെയിറ്റ് ലെഗ് റെയ്‌സ്",
        "description": "Lifting the fully straight leg upward while lying flat",
        "description_ml": "നേരെ കിടന്ന് കാൽ പൂർണ്ണമായി മുകളിലേക്ക് ഉയർത്തുന്നത്",
    },
    {
        "order": 5,
        "name": "Side-lying Leg Raise",
        "name_ml": "സൈഡ്-ലയിങ് ലെഗ് റെയ്‌സ്",
        "description": "Lifting the straight leg upward while lying on the unoperated side",
        "description_ml": "വശം തിരിഞ്ഞു കിടന്ന് കാൽ മുകളിലേക്ക് ഉയർത്തുന്നത്",
    },
    {
        "order": 6,
        "name": "Heel Slides",
        "name_ml": "ഹീൽ സ്ലൈഡ്സ്",
        "description": "Bending the knee by sliding the heel along the bed toward the body",
        "description_ml": "മലർന്നു കിടന്ന് കാൽമുട്ട് മടക്കി ഉപ്പൂറ്റി നിരക്കി കൊണ്ടുവരുന്നത്",
    },
    {
        "order": 7,
        "name": "Prone Leg Raise",
        "name_ml": "പ്രോൺ ലെഗ് റെയ്‌സ്",
        "description": "Lifting the straight leg backward while lying face down",
        "description_ml": "കമിഴ്ന്നു കിടന്ന് കാൽ പിന്നിലേക്ക് ഉയർത്തുന്നത്",
    },
    {
        "order": 8,
        "name": "Seated Assisted Knee Extension",
        "name_ml": "മുട്ട് മുന്നോട്ട് നിവർത്തുക",
        "description": "Sitting on the edge of the bed, using the unoperated leg to assist in straightening the knee forward",
        "description_ml": "കട്ടിലിന്റെ അരികിൽ ഇരുന്ന് മറ്റേ കാലിന്റെ സഹായത്തോടെ മുട്ട് മുന്നോട്ട് നിവർത്തുന്നത്",
    },
    {
        "order": 9,
        "name": "Seated Assisted Knee Flexion",
        "name_ml": "മുട്ട് പുറകിലേക്ക് മടക്കുക",
        "description": "Sitting on the edge of the bed, using the unoperated leg to assist in bending the knee backward",
        "description_ml": "കട്ടിലിന്റെ അരികിൽ ഇരുന്ന് മറ്റേ കാലിന്റെ സഹായത്തോടെ മുട്ട് പുറകിലേക്ക് മടക്കുന്നത്",
    },
]


class Command(BaseCommand):
    help = "Seed the database with the 9 default physiotherapy exercises."

    def handle(self, *args, **options):
        created_count = 0
        for ex_data in EXERCISES:
            _, created = Exercise.objects.update_or_create(
                order=ex_data["order"],
                defaults={
                    "name": ex_data["name"],
                    "name_ml": ex_data.get("name_ml", ""),
                    "description": ex_data["description"],
                    "description_ml": ex_data.get("description_ml", ""),
                },
            )
            if created:
                created_count += 1
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] {ex_data['name']}")

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! {created_count} created, {len(EXERCISES) - created_count} updated.")
        )
