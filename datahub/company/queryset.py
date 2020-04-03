from datahub.company.models import CompanyExportCountry, CompanyExportOverseasRegion, Contact


def get_contact_queryset():
    """Gets the contact query set used by views."""
    return Contact.objects.select_related(
        'title',
        'company',
        'adviser',
        'address_country',
        'archived_by',
    )


def get_export_country_queryset():
    """Gets the export country query set used by views."""
    return CompanyExportCountry.objects.order_by('pk').select_related('country')


def get_export_region_queryset():
    """Gets the export region query set used by views."""
    return CompanyExportOverseasRegion.objects.order_by('pk').select_related('region')
