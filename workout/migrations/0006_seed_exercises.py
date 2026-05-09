"""
Data migration: seed the 9 physiotherapy exercises.
Runs automatically with `manage.py migrate`, so every fresh
Git clone gets the exercise data out-of-the-box.
"""

from django.db import migrations


EXERCISES = [
    {
        "order": 1,
        "name": "Quad Sets",
        "name_ml": "ക്വാഡ് സെറ്റ്സ്",
        "description": "Pressing the knee down into a rolled towel",
        "description_ml": "മുട്ടിനടിയിൽ തുണി വെച്ച് താഴേക്ക് അമർത്തുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 2,
        "name": "Heel Props",
        "name_ml": "ഹീൽ പ്രോപ്സ്",
        "description": "Keeping the leg straight with a rolled towel under the heel",
        "description_ml": "ഉപ്പൂറ്റിക്കടിയിൽ തുണി വെച്ച് കാൽ നിവർത്തി വെക്കുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 3,
        "name": "Short Arc Quads (SAQ)",
        "name_ml": "ഷോർട്ട് ആർക്ക് ക്വാഡ്സ് (SAQ)",
        "description": "Lifting only the foot with a supportive pillow under the knee",
        "description_ml": "മുട്ടിനടിയിൽ പില്ലോ വെച്ച് പാദം മാത്രം ഉയർത്തുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 4,
        "name": "Straight Leg Raise (SLR)",
        "name_ml": "സ്ട്രെയിറ്റ് ലെഗ് റൈസ് (SLR)",
        "description": "Lifting the fully straight leg upward while lying flat",
        "description_ml": "നേരെ കിടന്ന് കാൽ പൂർണ്ണമായി മുകളിലേക്ക് ഉയർത്തുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 5,
        "name": "Side-lying Leg Raise",
        "name_ml": "സൈഡ്-ലൈയിങ് ലെഗ് റൈസ്",
        "description": "Lifting the straight leg upward while lying on the unoperated side",
        "description_ml": "വശം തിരിഞ്ഞു കിടന്ന് കാൽ മുകളിലേക്ക് ഉയർത്തുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 6,
        "name": "Heel Slides",
        "name_ml": "ഹീൽ സ്ലൈഡ്സ്",
        "description": "Bending the knee by sliding the heel along the bed toward the body",
        "description_ml": "മലർന്നു കിടന്ന് കാൽമുട്ട് മടക്കി ഉപ്പൂറ്റി നിരക്കി കൊണ്ടുവരുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 7,
        "name": "Prone Leg Raise",
        "name_ml": "പ്രോൺ ലെഗ് റൈസ്",
        "description": "Lifting the straight leg backward while lying face down",
        "description_ml": "കമിഴ്ന്നു കിടന്ന് കാൽ പിന്നിലേക്ക് ഉയർത്തുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 8,
        "name": "Seated Assisted Knee Extension",
        "name_ml": "സീറ്റഡ് അസിസ്റ്റഡ് നീ എക്സ്റ്റൻഷൻ",
        "description": "Sitting on the edge of the bed, using the unoperated leg to assist in straightening the knee forward",
        "description_ml": "കട്ടിലിന്റെ അരികിൽ ഇരുന്ന് മറ്റേ കാലിന്റെ സഹായത്തോടെ മുട്ട് മുന്നോട്ട് നിവർത്തുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
    {
        "order": 9,
        "name": "Seated Assisted Knee Flexion",
        "name_ml": "സീറ്റഡ് അസിസ്റ്റഡ് നീ ഫ്ലക്ഷൻ",
        "description": "Sitting on the edge of the bed, using the unoperated leg to assist in bending the knee backward",
        "description_ml": "കട്ടിലിന്റെ അരികിൽ ഇരുന്ന് മറ്റേ കാലിന്റെ സഹായത്തോടെ മുട്ട് പുറകിലേക്ക് മടക്കുന്നത്",
        "reps": 20,
        "hold_seconds": 10,
        "rest_seconds": 5,
    },
]


def seed_exercises(apps, schema_editor):
    """Insert all exercises if they don't already exist."""
    Exercise = apps.get_model("workout", "Exercise")
    for data in EXERCISES:
        Exercise.objects.get_or_create(order=data["order"], defaults=data)


def unseed_exercises(apps, schema_editor):
    """Remove the seeded exercises (used when reversing this migration)."""
    Exercise = apps.get_model("workout", "Exercise")
    orders = [e["order"] for e in EXERCISES]
    Exercise.objects.filter(order__in=orders).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("workout", "0005_exercise_name_ml"),
    ]

    operations = [
        migrations.RunPython(seed_exercises, reverse_code=unseed_exercises),
    ]
