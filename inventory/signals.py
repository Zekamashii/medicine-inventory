from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from pykakasi import kakasi
from inventory.models import UserProfile, Drug, Site, SafetyStock, DrugObsoleteBySite


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    try:
        if created:
            # Create a new UserProfile object associated with the User instance
            UserProfile.objects.create(user=instance)
        else:
            # Save the UserProfile object associated with the User instance
            instance.userprofile.save()
    except Exception as e:
        print(f"Error in create_or_update_user_profile signal: {e}")


@receiver(user_logged_in)
def set_default_site_cookie(sender, user, request, **kwargs):
    default_site_id = user.userprofile.default_site_id if user.userprofile.default_site else ''
    if default_site_id:
        request.session['default_site_id'] = default_site_id  # Temporarily store in the session


@receiver(post_save, sender=Drug)
def create_safety_stock_for_new_drug(sender, instance, created, **kwargs):
    if created:
        sites = Site.objects.all()
        for site in sites:
            SafetyStock.objects.create(drug=instance, site=site, min_stock=1)
            DrugObsoleteBySite.objects.create(drug=instance, site=site, is_obsolete=False)

            if not instance.kana and instance.name:
                kks = kakasi()
                kks.setMode("J", "H")  # Kanji to Hiragana
                kks.setMode('K', 'H')  # Katakana to Hiragana
                conv = kks.getConverter()
                instance.kana = conv.do(instance.name)
                instance.save()


@receiver(post_save, sender=Site)
def create_safety_stock_for_new_site(sender, instance, created, **kwargs):
    if created:
        drugs = Drug.objects.all()
        for drug in drugs:
            SafetyStock.objects.create(drug=drug, site=instance, min_stock=1)
            DrugObsoleteBySite.objects.create(drug=drug, site=instance, is_obsolete=False)
