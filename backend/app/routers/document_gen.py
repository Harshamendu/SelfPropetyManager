import io
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_admin, require_user
from app.models.contact import Contact
from app.models.document_template import DocumentTemplate
from app.models.property import Property
from app.schemas.document_template import (
    DocumentTemplateCreate,
    DocumentTemplateResponse,
    DocumentTemplateUpdate,
    GenerateDocumentRequest,
)

router = APIRouter(tags=["Document Generation"], dependencies=[Depends(require_user)])


@router.get(
    "/document-templates",
    response_model=list[DocumentTemplateResponse],
)
async def list_templates(
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(DocumentTemplate)
    if state:
        stmt = stmt.where(DocumentTemplate.state == state)
    stmt = stmt.order_by(DocumentTemplate.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/document-templates",
    response_model=DocumentTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_template(
    data: DocumentTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    template = DocumentTemplate(
        name=data.name,
        description=data.description,
        template_body=data.template_body,
        variables=[v.model_dump() for v in data.variables],
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get(
    "/document-templates/{template_id}",
    response_model=DocumentTemplateResponse,
)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    template = await db.get(DocumentTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put(
    "/document-templates/{template_id}",
    response_model=DocumentTemplateResponse,
    dependencies=[Depends(require_admin)],
)
async def update_template(
    template_id: UUID,
    data: DocumentTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    template = await db.get(DocumentTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = data.model_dump(exclude_unset=True)
    if "variables" in update_data and update_data["variables"] is not None:
        update_data["variables"] = [
            v.model_dump() for v in data.variables
        ]
    for key, value in update_data.items():
        setattr(template, key, value)

    await db.commit()
    await db.refresh(template)
    return template


@router.delete(
    "/document-templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    template = await db.get(DocumentTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(template)
    await db.commit()


@router.post(
    "/document-templates/seed/{state}",
    response_model=list[DocumentTemplateResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def seed_state_templates(
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Seed state-specific landlord document templates (upserts by name)."""
    state = state.upper()
    templates_data = _get_state_templates(state)
    if not templates_data:
        raise HTTPException(status_code=404, detail=f"No templates available for state: {state}")

    template_names = [t["name"] for t in templates_data]

    # Delete existing templates with the same names
    existing = await db.execute(
        select(DocumentTemplate).where(DocumentTemplate.name.in_(template_names))
    )
    for old in existing.scalars().all():
        await db.delete(old)
    await db.flush()

    created = []
    for t in templates_data:
        template = DocumentTemplate(
            name=t["name"],
            state=state,
            description=t["description"],
            template_body=t["template_body"],
            variables=t["variables"],
        )
        db.add(template)
        created.append(template)
    await db.commit()
    for t in created:
        await db.refresh(t)
    return created


def _get_state_templates(state: str) -> list[dict]:
    """Route to the correct state template set."""
    state_map = {
        "GA": _get_georgia_templates,
        # Add more states here as needed
        # "TX": _get_texas_templates,
        # "FL": _get_florida_templates,
    }
    func = state_map.get(state)
    return func() if func else []


def _get_georgia_templates() -> list[dict]:
    """Return all Georgia landlord document templates."""
    return [
        # 1. Residential Lease Agreement
        {
            "name": "Georgia Residential Lease Agreement",
            "description": "Standard residential lease agreement compliant with Georgia Landlord-Tenant Act (O.C.G.A. § 44-7)",
            "template_body": (
                "GEORGIA RESIDENTIAL LEASE AGREEMENT\n"
                "\n"
                "This Residential Lease Agreement (\"Agreement\") is entered into on {{effective_date}}, "
                "by and between:\n"
                "\n"
                "LANDLORD: {{landlord_name}}\n"
                "Address: {{landlord_address}}\n"
                "Phone: {{landlord_phone}}\n"
                "Email: {{landlord_email}}\n"
                "\n"
                "TENANT(S): {{tenant_name}}\n"
                "Current Address: {{tenant_current_address}}\n"
                "Phone: {{tenant_phone}}\n"
                "Email: {{tenant_email}}\n"
                "\n"
                "PROPERTY ADDRESS: {{property_address}}\n"
                "City: {{property_city}}, State: Georgia, ZIP: {{property_zip}}\n"
                "\n"
                "1. LEASE TERM\n"
                "This lease shall commence on {{lease_start_date}} and terminate on {{lease_end_date}}. "
                "This is a fixed-term lease. Upon expiration, this lease shall automatically convert to a "
                "month-to-month tenancy unless either party provides written notice of termination at least "
                "60 days prior to the desired termination date.\n"
                "\n"
                "2. RENT\n"
                "a) Monthly Rent: ${{monthly_rent}} per month.\n"
                "b) Due Date: Rent is due on the {{rent_due_day}} day of each month.\n"
                "c) Payment Method: {{payment_method}}\n"
                "d) Rent shall be payable to: {{landlord_name}}\n"
                "\n"
                "3. LATE FEES (Per O.C.G.A. § 44-7-2)\n"
                "If rent is not received by the {{late_fee_grace_days}} day after the due date, Tenant shall "
                "pay a late fee of ${{late_fee_amount}}. Georgia law does not cap late fees, but they must be "
                "reasonable and agreed upon in the lease.\n"
                "\n"
                "4. SECURITY DEPOSIT (Per O.C.G.A. § 44-7-30 through 44-7-37)\n"
                "a) Security Deposit Amount: ${{security_deposit}}\n"
                "b) The security deposit shall be held in an escrow account at {{escrow_bank_name}} as required "
                "for landlords owning more than 10 units, or shall be held by Landlord.\n"
                "c) Landlord shall provide Tenant with a written list of any pre-existing damage within 3 "
                "business days of move-in.\n"
                "d) Within one (1) month after lease termination and Tenant vacating the premises, Landlord "
                "shall return the deposit or provide an itemized statement of deductions.\n"
                "e) Permissible deductions include: unpaid rent, damage beyond normal wear and tear, and "
                "costs for Tenant's breach of this Agreement.\n"
                "\n"
                "5. UTILITIES AND SERVICES\n"
                "Tenant is responsible for: {{tenant_utilities}}\n"
                "Landlord is responsible for: {{landlord_utilities}}\n"
                "\n"
                "6. OCCUPANCY\n"
                "The premises shall be occupied exclusively by the following individuals:\n"
                "{{authorized_occupants}}\n"
                "No additional persons may reside in the property without Landlord's prior written consent.\n"
                "\n"
                "7. PETS\n"
                "{{pet_policy}}\n"
                "Pet deposit (if applicable): ${{pet_deposit}}\n"
                "Monthly pet rent (if applicable): ${{monthly_pet_rent}}\n"
                "\n"
                "8. MAINTENANCE AND REPAIRS (Per O.C.G.A. § 44-7-13 & 44-7-14)\n"
                "a) Landlord shall maintain the premises in a habitable condition and make all necessary "
                "repairs to keep the premises fit for human habitation.\n"
                "b) Tenant shall keep the premises clean, use all fixtures and appliances properly, and "
                "promptly notify Landlord of any needed repairs.\n"
                "c) Tenant shall not make alterations without Landlord's prior written consent.\n"
                "\n"
                "9. RIGHT OF ENTRY (Per O.C.G.A. § 44-7-25)\n"
                "Landlord or Landlord's agent may enter the premises upon reasonable notice (minimum 24 hours) "
                "for inspections, repairs, or to show the property to prospective tenants or buyers, except "
                "in case of emergency.\n"
                "\n"
                "10. TERMINATION AND DEFAULT\n"
                "a) Tenant Default: If Tenant fails to pay rent or violates any term of this Agreement, "
                "Landlord may provide notice and pursue remedies under Georgia law, including filing a "
                "dispossessory action (O.C.G.A. § 44-7-50).\n"
                "b) Landlord is not required to provide a cure period for nonpayment of rent in Georgia.\n"
                "c) Early Termination by Tenant: Tenant may terminate early by providing {{early_termination_notice}} "
                "days written notice and paying an early termination fee of ${{early_termination_fee}}.\n"
                "\n"
                "11. ABANDONMENT\n"
                "If the premises appear abandoned and rent is delinquent, Landlord may follow Georgia law "
                "(O.C.G.A. § 44-7-55) to reclaim the premises and dispose of abandoned property.\n"
                "\n"
                "12. INSURANCE\n"
                "Tenant is {{renter_insurance_required}} to maintain renter's insurance with a minimum "
                "coverage of ${{renter_insurance_min_coverage}}. Landlord's property insurance does not cover "
                "Tenant's personal belongings.\n"
                "\n"
                "13. LEAD-BASED PAINT DISCLOSURE\n"
                "If the property was built before 1978: {{lead_paint_disclosure}}\n"
                "\n"
                "14. FLOODING DISCLOSURE (Per O.C.G.A. § 44-7-20)\n"
                "Landlord discloses that the property {{flood_disclosure}} experienced flooding in the last "
                "five years.\n"
                "\n"
                "15. MOLD DISCLOSURE\n"
                "Landlord discloses: {{mold_disclosure}}\n"
                "\n"
                "16. GOVERNING LAW\n"
                "This Agreement shall be governed by the laws of the State of Georgia.\n"
                "\n"
                "17. ADDITIONAL TERMS\n"
                "{{additional_terms}}\n"
                "\n"
                "\n"
                "LANDLORD SIGNATURE: ________________________    Date: ____________\n"
                "Print Name: {{landlord_name}}\n"
                "\n"
                "TENANT SIGNATURE: ________________________     Date: ____________\n"
                "Print Name: {{tenant_name}}\n"
            ),
            "variables": [
                {"name": "effective_date", "label": "Effective Date"},
                {"name": "landlord_name", "label": "Landlord Full Name"},
                {"name": "landlord_address", "label": "Landlord Address"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "tenant_name", "label": "Tenant Full Name"},
                {"name": "tenant_current_address", "label": "Tenant Current Address"},
                {"name": "tenant_phone", "label": "Tenant Phone"},
                {"name": "tenant_email", "label": "Tenant Email"},
                {"name": "property_address", "label": "Property Street Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP Code"},
                {"name": "lease_start_date", "label": "Lease Start Date"},
                {"name": "lease_end_date", "label": "Lease End Date"},
                {"name": "monthly_rent", "label": "Monthly Rent Amount"},
                {"name": "rent_due_day", "label": "Rent Due Day (e.g., 1st)"},
                {"name": "payment_method", "label": "Payment Method (e.g., Check, Zelle, Direct Deposit)"},
                {"name": "late_fee_grace_days", "label": "Late Fee Grace Period (days)"},
                {"name": "late_fee_amount", "label": "Late Fee Amount"},
                {"name": "security_deposit", "label": "Security Deposit Amount"},
                {"name": "escrow_bank_name", "label": "Escrow Bank Name (if applicable)"},
                {"name": "tenant_utilities", "label": "Tenant-Paid Utilities"},
                {"name": "landlord_utilities", "label": "Landlord-Paid Utilities"},
                {"name": "authorized_occupants", "label": "Authorized Occupants (names)"},
                {"name": "pet_policy", "label": "Pet Policy (Allowed/Not Allowed/Restrictions)"},
                {"name": "pet_deposit", "label": "Pet Deposit", "default_value": "0"},
                {"name": "monthly_pet_rent", "label": "Monthly Pet Rent", "default_value": "0"},
                {"name": "early_termination_notice", "label": "Early Termination Notice (days)", "default_value": "60"},
                {"name": "early_termination_fee", "label": "Early Termination Fee"},
                {"name": "renter_insurance_required", "label": "Renter Insurance (required/encouraged)"},
                {"name": "renter_insurance_min_coverage", "label": "Min Insurance Coverage", "default_value": "100000"},
                {"name": "lead_paint_disclosure", "label": "Lead Paint Disclosure"},
                {"name": "flood_disclosure", "label": "Flood Disclosure (has/has not)"},
                {"name": "mold_disclosure", "label": "Mold Disclosure"},
                {"name": "additional_terms", "label": "Additional Terms"},
            ],
        },
        # 2. Lease Renewal Agreement
        {
            "name": "Georgia Lease Renewal Agreement",
            "description": "Lease renewal/extension agreement for existing tenants under Georgia law",
            "template_body": (
                "GEORGIA LEASE RENEWAL AGREEMENT\n"
                "\n"
                "This Lease Renewal Agreement (\"Renewal\") is entered into on {{effective_date}}, between:\n"
                "\n"
                "LANDLORD: {{landlord_name}}\n"
                "TENANT(S): {{tenant_name}}\n"
                "PROPERTY: {{property_address}}, {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "WHEREAS, the parties entered into a Residential Lease Agreement dated {{original_lease_date}} "
                "(\"Original Lease\"), which is set to expire on {{current_lease_end_date}};\n"
                "\n"
                "WHEREAS, both parties desire to renew the lease under the following terms;\n"
                "\n"
                "NOW, THEREFORE, the parties agree as follows:\n"
                "\n"
                "1. RENEWAL TERM\n"
                "The lease is hereby renewed for a period commencing {{new_lease_start_date}} and ending "
                "{{new_lease_end_date}}.\n"
                "\n"
                "2. RENT ADJUSTMENT\n"
                "Monthly rent for the renewal term shall be ${{new_monthly_rent}} (previously ${{old_monthly_rent}}).\n"
                "This represents a {{rent_change_reason}}.\n"
                "\n"
                "3. MODIFIED TERMS\n"
                "The following terms of the Original Lease are modified for this renewal:\n"
                "{{modified_terms}}\n"
                "\n"
                "4. ALL OTHER TERMS\n"
                "All other terms and conditions of the Original Lease shall remain in full force and effect "
                "and are incorporated herein by reference.\n"
                "\n"
                "5. SECURITY DEPOSIT\n"
                "The existing security deposit of ${{security_deposit}} shall continue to be held and applied "
                "under the terms of the Original Lease. {{additional_deposit_terms}}\n"
                "\n"
                "\n"
                "LANDLORD SIGNATURE: ________________________    Date: ____________\n"
                "Print Name: {{landlord_name}}\n"
                "\n"
                "TENANT SIGNATURE: ________________________     Date: ____________\n"
                "Print Name: {{tenant_name}}\n"
            ),
            "variables": [
                {"name": "effective_date", "label": "Effective Date"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "original_lease_date", "label": "Original Lease Date"},
                {"name": "current_lease_end_date", "label": "Current Lease End Date"},
                {"name": "new_lease_start_date", "label": "New Lease Start Date"},
                {"name": "new_lease_end_date", "label": "New Lease End Date"},
                {"name": "new_monthly_rent", "label": "New Monthly Rent"},
                {"name": "old_monthly_rent", "label": "Previous Monthly Rent"},
                {"name": "rent_change_reason", "label": "Rent Change Reason"},
                {"name": "modified_terms", "label": "Modified Terms (list changes)"},
                {"name": "security_deposit", "label": "Existing Security Deposit"},
                {"name": "additional_deposit_terms", "label": "Additional Deposit Terms", "default_value": "No additional deposit required."},
            ],
        },
        # 2b. Lease Renewal Notice (friendly letter format)
        {
            "name": "Georgia Lease Renewal Notice",
            "description": "Friendly letter to tenant notifying lease expiration and offering renewal with updated rent",
            "template_body": (
                "{{notice_date}}\n"
                "\n"
                "{{property_address}}, {{property_city}}, {{property_state}} - {{property_zip}}\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "This letter is to inform you that your current lease for the property located at "
                "{{property_address}} will expire on {{current_lease_end_date}}.\n"
                "\n"
                "We have enjoyed having you as a tenant and would like to offer you the opportunity to "
                "renew your lease for another {{renewal_term_options}}.\n"
                "\n"
                "If you choose to renew, the new monthly rent will be USD {{new_monthly_rent}}, effective "
                "{{new_lease_start_date}}. All other terms of the lease will remain the same unless a new "
                "lease agreement is signed. {{rent_increase_reason}}\n"
                "\n"
                "Please let us know in writing whether you accept or decline this offer by "
                "{{response_deadline}} (30 days before lease ends).\n"
                "\n"
                "If you accept, we will prepare a new lease agreement for you to sign.\n"
                "\n"
                "Please remember that you will need to vacate the premises by {{current_lease_end_date}} "
                "if you decide not to renew. Please provide us with a forwarding address so we can return "
                "your security deposit after a final inspection and assessment of any damages, in "
                "accordance with the terms of your current lease.\n"
                "\n"
                "If you have any questions, please do not hesitate to contact me at {{landlord_phone}} or "
                "{{landlord_email}}.\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "{{landlord_name}}\n"
            ),
            "variables": [
                {"name": "notice_date", "label": "Notice Date"},
                {"name": "property_address", "label": "Property Street Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_state", "label": "Property State", "default_value": "GA"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "tenant_name", "label": "Tenant Name(s)"},
                {"name": "current_lease_end_date", "label": "Current Lease End Date"},
                {"name": "renewal_term_options", "label": "Renewal Term Options", "default_value": "12 months or 24 months"},
                {"name": "new_monthly_rent", "label": "New Monthly Rent"},
                {"name": "new_lease_start_date", "label": "New Lease Start Date"},
                {"name": "rent_increase_reason", "label": "Reason for Rent Increase", "default_value": "This adjustment is necessary due to an increase in property taxes and maintenance costs."},
                {"name": "response_deadline", "label": "Response Deadline (30 days before lease end)"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "landlord_name", "label": "Landlord Name"},
            ],
        },
        # 3. Notice to Pay Rent or Quit
        {
            "name": "Georgia Demand for Rent / Notice to Pay or Quit",
            "description": "Formal demand for unpaid rent per O.C.G.A. § 44-7-50 (Georgia has no mandatory cure period but notice is best practice)",
            "template_body": (
                "NOTICE TO PAY RENT OR VACATE\n"
                "(Pursuant to Georgia Landlord-Tenant Law)\n"
                "\n"
                "Date: {{notice_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{property_address}}\n"
                "    {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "FROM: {{landlord_name}} (\"Landlord\")\n"
                "\n"
                "RE: DEMAND FOR PAYMENT OF PAST DUE RENT\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "Please be advised that as of {{notice_date}}, you are in default of your Residential Lease "
                "Agreement dated {{lease_date}} for the above-referenced property.\n"
                "\n"
                "AMOUNT DUE:\n"
                "  Rent for {{delinquent_months}}: ${{delinquent_rent_amount}}\n"
                "  Late Fees: ${{late_fees}}\n"
                "  Other Charges: ${{other_charges}} ({{other_charges_description}})\n"
                "  TOTAL DUE: ${{total_amount_due}}\n"
                "\n"
                "DEMAND:\n"
                "You are hereby demanded to pay the total amount of ${{total_amount_due}} within "
                "{{demand_days}} days of this notice, or to vacate the premises.\n"
                "\n"
                "NOTICE:\n"
                "Under Georgia law (O.C.G.A. § 44-7-50), a landlord is not required to provide a cure "
                "period before filing a dispossessory action. This notice is provided as a courtesy to "
                "give you an opportunity to resolve this matter without court involvement.\n"
                "\n"
                "If payment is not received by {{payment_deadline_date}}, Landlord will pursue all legal "
                "remedies available, including but not limited to filing a dispossessory action in the "
                "Magistrate Court of {{county_name}} County, Georgia, seeking possession of the premises, "
                "all past-due rent, late fees, court costs, and attorney's fees as permitted by the lease "
                "agreement.\n"
                "\n"
                "Payment may be made by: {{payment_instructions}}\n"
                "\n"
                "This notice is not a waiver of any rights Landlord may have under the lease or Georgia law.\n"
                "\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
                "{{landlord_phone}}\n"
                "{{landlord_email}}\n"
                "\n"
                "CERTIFICATE OF SERVICE\n"
                "I certify that a copy of this notice was delivered on {{notice_date}} by:\n"
                "[ ] Hand delivery to the tenant\n"
                "[ ] Posted on the front door of the premises\n"
                "[ ] Sent via certified mail, return receipt requested\n"
            ),
            "variables": [
                {"name": "notice_date", "label": "Notice Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "lease_date", "label": "Original Lease Date"},
                {"name": "delinquent_months", "label": "Delinquent Month(s) (e.g., March 2026, April 2026)"},
                {"name": "delinquent_rent_amount", "label": "Past Due Rent Amount"},
                {"name": "late_fees", "label": "Late Fees"},
                {"name": "other_charges", "label": "Other Charges Amount", "default_value": "0"},
                {"name": "other_charges_description", "label": "Other Charges Description", "default_value": "N/A"},
                {"name": "total_amount_due", "label": "Total Amount Due"},
                {"name": "demand_days", "label": "Days to Pay or Vacate", "default_value": "3"},
                {"name": "payment_deadline_date", "label": "Payment Deadline Date"},
                {"name": "county_name", "label": "County Name"},
                {"name": "payment_instructions", "label": "Payment Instructions"},
            ],
        },
        # 4. Notice of Lease Non-Renewal / Termination
        {
            "name": "Georgia Notice of Lease Non-Renewal",
            "description": "Notice to tenant of lease non-renewal per O.C.G.A. § 44-7-7 (60-day notice for month-to-month)",
            "template_body": (
                "NOTICE OF LEASE NON-RENEWAL / TERMINATION\n"
                "\n"
                "Date: {{notice_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{property_address}}\n"
                "    {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "FROM: {{landlord_name}} (\"Landlord\")\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "This letter serves as formal notice that your {{lease_type}} tenancy at the above-referenced "
                "property will NOT be renewed and will terminate on {{termination_date}}.\n"
                "\n"
                "Under Georgia law (O.C.G.A. § 44-7-7), a tenancy at will (month-to-month) may be "
                "terminated by either party by giving 60 days' written notice. For fixed-term leases, "
                "termination occurs at the end of the lease term.\n"
                "\n"
                "MOVE-OUT REQUIREMENTS:\n"
                "1. All personal belongings must be removed by {{termination_date}}.\n"
                "2. The premises must be returned in the same condition as received, less normal wear and tear.\n"
                "3. All keys, garage openers, and access devices must be returned to Landlord.\n"
                "4. Forwarding address must be provided in writing for security deposit return.\n"
                "5. A move-out inspection will be scheduled on or near {{termination_date}}.\n"
                "\n"
                "SECURITY DEPOSIT:\n"
                "Your security deposit of ${{security_deposit}} will be handled per Georgia law "
                "(O.C.G.A. § 44-7-34). Within one month of vacating, Landlord will either return the "
                "deposit or provide an itemized statement of deductions.\n"
                "\n"
                "Reason for non-renewal: {{non_renewal_reason}}\n"
                "\n"
                "If you have any questions, please contact me at {{landlord_phone}} or {{landlord_email}}.\n"
                "\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
            ),
            "variables": [
                {"name": "notice_date", "label": "Notice Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "lease_type", "label": "Lease Type (month-to-month / fixed-term)"},
                {"name": "termination_date", "label": "Termination Date"},
                {"name": "security_deposit", "label": "Security Deposit Amount"},
                {"name": "non_renewal_reason", "label": "Reason for Non-Renewal"},
            ],
        },
        # 5. Security Deposit Return Letter
        {
            "name": "Georgia Security Deposit Return Letter",
            "description": "Itemized security deposit return/deduction statement per O.C.G.A. § 44-7-34",
            "template_body": (
                "SECURITY DEPOSIT RETURN STATEMENT\n"
                "(Per O.C.G.A. § 44-7-34)\n"
                "\n"
                "Date: {{statement_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{tenant_forwarding_address}}\n"
                "\n"
                "FROM: {{landlord_name}}\n"
                "\n"
                "PROPERTY: {{property_address}}, {{property_city}}, Georgia {{property_zip}}\n"
                "LEASE DATES: {{lease_start_date}} through {{lease_end_date}}\n"
                "MOVE-OUT DATE: {{moveout_date}}\n"
                "\n"
                "SECURITY DEPOSIT ACCOUNTING:\n"
                "\n"
                "Original Security Deposit: ${{original_deposit}}\n"
                "\n"
                "ITEMIZED DEDUCTIONS:\n"
                "{{deductions_list}}\n"
                "\n"
                "Total Deductions: ${{total_deductions}}\n"
                "\n"
                "AMOUNT RETURNED TO TENANT: ${{amount_returned}}\n"
                "\n"
                "{{refund_method}}\n"
                "\n"
                "NOTES:\n"
                "Per Georgia law (O.C.G.A. § 44-7-34), this statement is provided within one month of "
                "the tenant vacating the premises. The landlord conducted a move-out inspection on "
                "{{inspection_date}}. A pre-move-in inspection list was provided to the tenant at the "
                "start of the tenancy as required by O.C.G.A. § 44-7-33.\n"
                "\n"
                "If you dispute any deductions, you may contact the Landlord within 30 days. If unresolved, "
                "either party may pursue the matter in Magistrate Court.\n"
                "\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
                "{{landlord_phone}}\n"
                "{{landlord_email}}\n"
            ),
            "variables": [
                {"name": "statement_date", "label": "Statement Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "tenant_forwarding_address", "label": "Tenant Forwarding Address"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "lease_start_date", "label": "Lease Start Date"},
                {"name": "lease_end_date", "label": "Lease End Date"},
                {"name": "moveout_date", "label": "Move-Out Date"},
                {"name": "original_deposit", "label": "Original Deposit Amount"},
                {"name": "deductions_list", "label": "Itemized Deductions (e.g., Carpet cleaning: $150, Wall repair: $200)"},
                {"name": "total_deductions", "label": "Total Deductions"},
                {"name": "amount_returned", "label": "Amount Returned to Tenant"},
                {"name": "refund_method", "label": "Refund Method (e.g., Check enclosed, Zelle sent)"},
                {"name": "inspection_date", "label": "Move-Out Inspection Date"},
            ],
        },
        # 6. Move-In / Move-Out Inspection Checklist
        {
            "name": "Georgia Move-In / Move-Out Inspection Checklist",
            "description": "Property condition checklist required by O.C.G.A. § 44-7-33 for security deposit protection",
            "template_body": (
                "MOVE-IN / MOVE-OUT INSPECTION CHECKLIST\n"
                "(Required per O.C.G.A. § 44-7-33)\n"
                "\n"
                "PROPERTY: {{property_address}}, {{property_city}}, Georgia {{property_zip}}\n"
                "TENANT: {{tenant_name}}\n"
                "INSPECTION TYPE: {{inspection_type}}\n"
                "DATE: {{inspection_date}}\n"
                "\n"
                "IMPORTANT: Under Georgia law, the landlord must provide the tenant with a written list of "
                "pre-existing damage within 3 business days of move-in. Failure to do so may limit the "
                "landlord's ability to make deductions from the security deposit.\n"
                "\n"
                "LIVING ROOM / COMMON AREAS:\n"
                "  Walls & Paint: {{living_walls}}\n"
                "  Flooring: {{living_flooring}}\n"
                "  Windows & Blinds: {{living_windows}}\n"
                "  Light Fixtures: {{living_lights}}\n"
                "  Electrical Outlets: {{living_outlets}}\n"
                "  Ceiling / Ceiling Fan: {{living_ceiling}}\n"
                "\n"
                "KITCHEN:\n"
                "  Countertops & Cabinets: {{kitchen_counters}}\n"
                "  Stove / Oven: {{kitchen_stove}}\n"
                "  Refrigerator: {{kitchen_fridge}}\n"
                "  Dishwasher: {{kitchen_dishwasher}}\n"
                "  Sink & Faucet: {{kitchen_sink}}\n"
                "  Flooring: {{kitchen_flooring}}\n"
                "\n"
                "BEDROOM(S):\n"
                "  Walls & Paint: {{bedroom_walls}}\n"
                "  Flooring: {{bedroom_flooring}}\n"
                "  Closets & Doors: {{bedroom_closets}}\n"
                "  Windows & Blinds: {{bedroom_windows}}\n"
                "\n"
                "BATHROOM(S):\n"
                "  Toilet: {{bathroom_toilet}}\n"
                "  Shower / Tub: {{bathroom_shower}}\n"
                "  Sink & Vanity: {{bathroom_sink}}\n"
                "  Mirrors: {{bathroom_mirrors}}\n"
                "  Exhaust Fan: {{bathroom_fan}}\n"
                "\n"
                "EXTERIOR / OTHER:\n"
                "  Front Door & Locks: {{exterior_door}}\n"
                "  Garage / Parking: {{exterior_garage}}\n"
                "  Yard / Landscaping: {{exterior_yard}}\n"
                "  HVAC System: {{hvac}}\n"
                "  Water Heater: {{water_heater}}\n"
                "  Smoke / CO Detectors: {{smoke_detectors}}\n"
                "\n"
                "ADDITIONAL NOTES:\n"
                "{{additional_notes}}\n"
                "\n"
                "\n"
                "LANDLORD SIGNATURE: ________________________    Date: ____________\n"
                "Print Name: {{landlord_name}}\n"
                "\n"
                "TENANT SIGNATURE: ________________________     Date: ____________\n"
                "Print Name: {{tenant_name}}\n"
            ),
            "variables": [
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "inspection_type", "label": "Inspection Type (Move-In / Move-Out)"},
                {"name": "inspection_date", "label": "Inspection Date"},
                {"name": "living_walls", "label": "Living Room - Walls & Paint Condition"},
                {"name": "living_flooring", "label": "Living Room - Flooring Condition"},
                {"name": "living_windows", "label": "Living Room - Windows & Blinds"},
                {"name": "living_lights", "label": "Living Room - Light Fixtures"},
                {"name": "living_outlets", "label": "Living Room - Electrical Outlets"},
                {"name": "living_ceiling", "label": "Living Room - Ceiling / Fan"},
                {"name": "kitchen_counters", "label": "Kitchen - Countertops & Cabinets"},
                {"name": "kitchen_stove", "label": "Kitchen - Stove / Oven"},
                {"name": "kitchen_fridge", "label": "Kitchen - Refrigerator"},
                {"name": "kitchen_dishwasher", "label": "Kitchen - Dishwasher"},
                {"name": "kitchen_sink", "label": "Kitchen - Sink & Faucet"},
                {"name": "kitchen_flooring", "label": "Kitchen - Flooring"},
                {"name": "bedroom_walls", "label": "Bedroom - Walls & Paint"},
                {"name": "bedroom_flooring", "label": "Bedroom - Flooring"},
                {"name": "bedroom_closets", "label": "Bedroom - Closets & Doors"},
                {"name": "bedroom_windows", "label": "Bedroom - Windows & Blinds"},
                {"name": "bathroom_toilet", "label": "Bathroom - Toilet"},
                {"name": "bathroom_shower", "label": "Bathroom - Shower / Tub"},
                {"name": "bathroom_sink", "label": "Bathroom - Sink & Vanity"},
                {"name": "bathroom_mirrors", "label": "Bathroom - Mirrors"},
                {"name": "bathroom_fan", "label": "Bathroom - Exhaust Fan"},
                {"name": "exterior_door", "label": "Front Door & Locks"},
                {"name": "exterior_garage", "label": "Garage / Parking"},
                {"name": "exterior_yard", "label": "Yard / Landscaping"},
                {"name": "hvac", "label": "HVAC System"},
                {"name": "water_heater", "label": "Water Heater"},
                {"name": "smoke_detectors", "label": "Smoke / CO Detectors"},
                {"name": "additional_notes", "label": "Additional Notes"},
            ],
        },
        # 7. Late Rent Notice
        {
            "name": "Georgia Late Rent Notice",
            "description": "Formal notice of late rent payment with fee assessment",
            "template_body": (
                "LATE RENT NOTICE\n"
                "\n"
                "Date: {{notice_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{property_address}}\n"
                "    {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "FROM: {{landlord_name}}\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "This letter is to inform you that your rent payment for the month of {{rent_month}} "
                "has not been received as of {{notice_date}}.\n"
                "\n"
                "Per your lease agreement dated {{lease_date}}:\n"
                "  Monthly Rent: ${{monthly_rent}}\n"
                "  Due Date: {{rent_due_day}} of each month\n"
                "  Grace Period: {{grace_period}} days\n"
                "  Late Fee: ${{late_fee}}\n"
                "\n"
                "AMOUNT NOW DUE:\n"
                "  Rent: ${{monthly_rent}}\n"
                "  Late Fee: ${{late_fee}}\n"
                "  Previous Balance: ${{previous_balance}}\n"
                "  TOTAL DUE: ${{total_due}}\n"
                "\n"
                "Please remit payment immediately via {{payment_method}}.\n"
                "\n"
                "This notice is a reminder and courtesy. Continued non-payment may result in further "
                "action under Georgia law, including the filing of a dispossessory proceeding.\n"
                "\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
                "{{landlord_phone}}\n"
            ),
            "variables": [
                {"name": "notice_date", "label": "Notice Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "lease_date", "label": "Lease Date"},
                {"name": "rent_month", "label": "Delinquent Month (e.g., March 2026)"},
                {"name": "monthly_rent", "label": "Monthly Rent"},
                {"name": "rent_due_day", "label": "Rent Due Day"},
                {"name": "grace_period", "label": "Grace Period (days)"},
                {"name": "late_fee", "label": "Late Fee Amount"},
                {"name": "previous_balance", "label": "Previous Balance", "default_value": "0.00"},
                {"name": "total_due", "label": "Total Amount Due"},
                {"name": "payment_method", "label": "Payment Method"},
            ],
        },
        # 8. Notice to Enter / Right of Entry
        {
            "name": "Georgia Notice to Enter Premises",
            "description": "24-hour advance notice to enter rental property per O.C.G.A. § 44-7-25",
            "template_body": (
                "NOTICE OF INTENT TO ENTER PREMISES\n"
                "(Per O.C.G.A. § 44-7-25)\n"
                "\n"
                "Date: {{notice_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{property_address}}\n"
                "    {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "FROM: {{landlord_name}}\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "This letter serves as formal notice that the Landlord or Landlord's authorized agent "
                "intends to enter the above-referenced premises on:\n"
                "\n"
                "DATE: {{entry_date}}\n"
                "TIME: {{entry_time}}\n"
                "ESTIMATED DURATION: {{estimated_duration}}\n"
                "\n"
                "PURPOSE OF ENTRY:\n"
                "{{entry_purpose}}\n"
                "\n"
                "PERSON(S) ENTERING:\n"
                "{{entering_persons}}\n"
                "\n"
                "Under Georgia law, landlords must provide reasonable notice before entering a tenant's "
                "premises except in cases of emergency. Your presence is not required but you are welcome "
                "to be present.\n"
                "\n"
                "If the scheduled time is inconvenient, please contact me at {{landlord_phone}} or "
                "{{landlord_email}} to arrange an alternative time.\n"
                "\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
            ),
            "variables": [
                {"name": "notice_date", "label": "Notice Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "entry_date", "label": "Planned Entry Date"},
                {"name": "entry_time", "label": "Planned Entry Time"},
                {"name": "estimated_duration", "label": "Estimated Duration"},
                {"name": "entry_purpose", "label": "Purpose of Entry (e.g., Scheduled maintenance, Annual inspection)"},
                {"name": "entering_persons", "label": "Person(s) Entering (e.g., Landlord, Licensed plumber - ABC Plumbing)"},
            ],
        },
        # 9. Rent Increase Notice
        {
            "name": "Georgia Rent Increase Notice",
            "description": "Notice of rent increase for month-to-month tenancy (60-day notice required per O.C.G.A. § 44-7-7)",
            "template_body": (
                "NOTICE OF RENT INCREASE\n"
                "\n"
                "Date: {{notice_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{property_address}}\n"
                "    {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "FROM: {{landlord_name}}\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "This letter serves as formal notice that the monthly rent for the above-referenced "
                "property will be increased effective {{effective_date}}.\n"
                "\n"
                "  Current Monthly Rent: ${{current_rent}}\n"
                "  New Monthly Rent: ${{new_rent}}\n"
                "  Increase Amount: ${{increase_amount}}\n"
                "\n"
                "Reason for increase: {{increase_reason}}\n"
                "\n"
                "Per Georgia law (O.C.G.A. § 44-7-7), this notice is being provided at least 60 days in "
                "advance of the effective date for month-to-month tenancies. Georgia does not have rent "
                "control, and there is no statutory limit on rent increases.\n"
                "\n"
                "If you agree to the new rent amount, no action is required — your continued tenancy after "
                "{{effective_date}} constitutes acceptance. If you do not agree, you may provide 60 days' "
                "written notice to terminate your tenancy.\n"
                "\n"
                "All other terms and conditions of your lease agreement remain unchanged.\n"
                "\n"
                "Please contact me at {{landlord_phone}} or {{landlord_email}} with any questions.\n"
                "\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
            ),
            "variables": [
                {"name": "notice_date", "label": "Notice Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "current_rent", "label": "Current Monthly Rent"},
                {"name": "new_rent", "label": "New Monthly Rent"},
                {"name": "increase_amount", "label": "Increase Amount"},
                {"name": "effective_date", "label": "Effective Date"},
                {"name": "increase_reason", "label": "Reason for Increase"},
            ],
        },
        # 10. Lease Violation Notice
        {
            "name": "Georgia Lease Violation Notice",
            "description": "Notice of lease violation with cure demand",
            "template_body": (
                "NOTICE OF LEASE VIOLATION\n"
                "\n"
                "Date: {{notice_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{property_address}}\n"
                "    {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "FROM: {{landlord_name}}\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "This letter serves as formal notice that you are in violation of your Residential Lease "
                "Agreement dated {{lease_date}} for the above-referenced property.\n"
                "\n"
                "VIOLATION:\n"
                "{{violation_description}}\n"
                "\n"
                "LEASE PROVISION VIOLATED:\n"
                "{{lease_section}}\n"
                "\n"
                "DATE(S) OF VIOLATION:\n"
                "{{violation_dates}}\n"
                "\n"
                "REQUIRED ACTION:\n"
                "You must cure this violation by {{cure_deadline}} by taking the following action:\n"
                "{{required_action}}\n"
                "\n"
                "WARNING:\n"
                "If this violation is not cured by the deadline stated above, Landlord may pursue all "
                "remedies available under Georgia law, including but not limited to:\n"
                "- Filing a dispossessory action (eviction) under O.C.G.A. § 44-7-50\n"
                "- Seeking damages for any costs incurred due to the violation\n"
                "- Termination of the lease agreement\n"
                "\n"
                "This is the {{violation_count}} notice for this type of violation. Repeated violations "
                "may result in immediate lease termination.\n"
                "\n"
                "Please contact me at {{landlord_phone}} or {{landlord_email}} to discuss.\n"
                "\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
            ),
            "variables": [
                {"name": "notice_date", "label": "Notice Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "lease_date", "label": "Original Lease Date"},
                {"name": "violation_description", "label": "Description of Violation"},
                {"name": "lease_section", "label": "Lease Section Violated"},
                {"name": "violation_dates", "label": "Date(s) of Violation"},
                {"name": "cure_deadline", "label": "Cure Deadline Date"},
                {"name": "required_action", "label": "Required Corrective Action"},
                {"name": "violation_count", "label": "Violation Count (1st, 2nd, 3rd)", "default_value": "1st"},
            ],
        },
        # 11. Rent Receipt
        {
            "name": "Georgia Rent Receipt",
            "description": "Official rent payment receipt for tenant records",
            "template_body": (
                "RENT RECEIPT\n"
                "\n"
                "Receipt Number: {{receipt_number}}\n"
                "Date: {{receipt_date}}\n"
                "\n"
                "RECEIVED FROM: {{tenant_name}}\n"
                "PROPERTY: {{property_address}}, {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "PAYMENT DETAILS:\n"
                "  Amount Received: ${{amount_received}}\n"
                "  Payment For: {{payment_period}} rent\n"
                "  Payment Method: {{payment_method}}\n"
                "  Check/Reference Number: {{reference_number}}\n"
                "\n"
                "BALANCE:\n"
                "  Monthly Rent: ${{monthly_rent}}\n"
                "  Amount Paid: ${{amount_received}}\n"
                "  Previous Balance: ${{previous_balance}}\n"
                "  Remaining Balance: ${{remaining_balance}}\n"
                "\n"
                "\n"
                "Received by:\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
                "{{landlord_phone}}\n"
            ),
            "variables": [
                {"name": "receipt_number", "label": "Receipt Number"},
                {"name": "receipt_date", "label": "Receipt Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "amount_received", "label": "Amount Received"},
                {"name": "payment_period", "label": "Payment Period (e.g., March 2026)"},
                {"name": "payment_method", "label": "Payment Method"},
                {"name": "reference_number", "label": "Check/Reference Number", "default_value": "N/A"},
                {"name": "monthly_rent", "label": "Monthly Rent"},
                {"name": "previous_balance", "label": "Previous Balance", "default_value": "0.00"},
                {"name": "remaining_balance", "label": "Remaining Balance", "default_value": "0.00"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
            ],
        },
        # 12. Maintenance Request Acknowledgment
        {
            "name": "Georgia Maintenance Request Acknowledgment",
            "description": "Written acknowledgment of tenant maintenance request with timeline",
            "template_body": (
                "MAINTENANCE REQUEST ACKNOWLEDGMENT\n"
                "\n"
                "Date: {{acknowledgment_date}}\n"
                "\n"
                "TO: {{tenant_name}}\n"
                "    {{property_address}}\n"
                "    {{property_city}}, Georgia {{property_zip}}\n"
                "\n"
                "FROM: {{landlord_name}}\n"
                "\n"
                "Dear {{tenant_name}},\n"
                "\n"
                "This letter acknowledges receipt of your maintenance request submitted on "
                "{{request_date}} regarding:\n"
                "\n"
                "ISSUE REPORTED:\n"
                "{{issue_description}}\n"
                "\n"
                "LOCATION IN PROPERTY:\n"
                "{{issue_location}}\n"
                "\n"
                "PRIORITY LEVEL: {{priority_level}}\n"
                "\n"
                "ACTION PLAN:\n"
                "{{action_plan}}\n"
                "\n"
                "ESTIMATED COMPLETION: {{estimated_completion}}\n"
                "\n"
                "ASSIGNED TO: {{assigned_contractor}}\n"
                "CONTRACTOR PHONE: {{contractor_phone}}\n"
                "\n"
                "ACCESS INSTRUCTIONS:\n"
                "{{access_instructions}}\n"
                "\n"
                "Per O.C.G.A. § 44-7-13, the landlord is responsible for maintaining the premises in a "
                "habitable condition. We take all maintenance requests seriously and will address this "
                "matter promptly.\n"
                "\n"
                "If the issue worsens or poses an immediate health/safety risk, contact me immediately "
                "at {{landlord_phone}}.\n"
                "\n"
                "\n"
                "Sincerely,\n"
                "\n"
                "________________________\n"
                "{{landlord_name}}\n"
                "{{landlord_email}}\n"
            ),
            "variables": [
                {"name": "acknowledgment_date", "label": "Acknowledgment Date"},
                {"name": "tenant_name", "label": "Tenant Name"},
                {"name": "property_address", "label": "Property Address"},
                {"name": "property_city", "label": "Property City"},
                {"name": "property_zip", "label": "Property ZIP"},
                {"name": "landlord_name", "label": "Landlord Name"},
                {"name": "landlord_phone", "label": "Landlord Phone"},
                {"name": "landlord_email", "label": "Landlord Email"},
                {"name": "request_date", "label": "Request Date"},
                {"name": "issue_description", "label": "Issue Description"},
                {"name": "issue_location", "label": "Location in Property"},
                {"name": "priority_level", "label": "Priority (Emergency / Urgent / Standard)"},
                {"name": "action_plan", "label": "Action Plan"},
                {"name": "estimated_completion", "label": "Estimated Completion Date"},
                {"name": "assigned_contractor", "label": "Assigned Contractor/Vendor"},
                {"name": "contractor_phone", "label": "Contractor Phone"},
                {"name": "access_instructions", "label": "Access Instructions (e.g., Tenant will be home, use lockbox)"},
            ],
        },
    ]


@router.get("/document-templates/context/{property_id}")
async def get_template_context(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get property, tenant, and landlord info for auto-filling templates."""
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    today = date.today()

    # Find active tenant with current lease
    tenant_result = await db.execute(
        select(Contact).where(
            Contact.property_id == property_id,
            Contact.contact_type == "tenant",
            Contact.is_active == True,  # noqa: E712
        ).order_by(Contact.lease_end.desc())
    )
    tenant = tenant_result.scalars().first()

    context: dict[str, str] = {
        # Property fields
        "property_address": prop.address_line1,
        "property_city": prop.city,
        "property_state": prop.state,
        "property_zip": prop.zip_code,
        "property_name": prop.name,
        "property_type": prop.property_type,
    }

    # Tenant fields
    if tenant:
        context.update({
            "tenant_name": f"{tenant.first_name} {tenant.last_name}",
            "tenant_phone": tenant.phone or "",
            "tenant_email": tenant.email or "",
            "tenant_current_address": tenant.address or "",
            "lease_start_date": str(tenant.lease_start) if tenant.lease_start else "",
            "lease_end_date": str(tenant.lease_end) if tenant.lease_end else "",
            "lease_start": str(tenant.lease_start) if tenant.lease_start else "",
            "lease_end": str(tenant.lease_end) if tenant.lease_end else "",
            "monthly_rent": str(tenant.monthly_rent) if tenant.monthly_rent else "",
            "authorized_occupants": f"{tenant.first_name} {tenant.last_name}",
        })
        # Lease date for original lease
        if tenant.lease_start:
            context["lease_date"] = str(tenant.lease_start)
            context["original_lease_date"] = str(tenant.lease_start)
        if tenant.lease_end:
            context["current_lease_end_date"] = str(tenant.lease_end)

    # Landlord fields from property
    if prop.landlord_name:
        context["landlord_name"] = prop.landlord_name
    if prop.landlord_phone:
        context["landlord_phone"] = prop.landlord_phone
    if prop.landlord_email:
        context["landlord_email"] = prop.landlord_email
    if prop.landlord_address:
        context["landlord_address"] = prop.landlord_address

    # Common defaults
    context.setdefault("effective_date", str(today))
    context.setdefault("notice_date", str(today))
    context.setdefault("statement_date", str(today))
    context.setdefault("receipt_date", str(today))
    context.setdefault("acknowledgment_date", str(today))
    context.setdefault("inspection_date", str(today))

    if prop.purchase_date:
        context["purchase_date"] = str(prop.purchase_date)

    return context


def _render_template_body(template: DocumentTemplate, variables: dict[str, str]) -> str:
    body = template.template_body
    for var_name, var_value in variables.items():
        body = body.replace(f"{{{{{var_name}}}}}", var_value or "")
    return body


@router.post("/document-templates/{template_id}/preview")
async def preview_document(
    template_id: UUID,
    request: GenerateDocumentRequest,
    db: AsyncSession = Depends(get_db),
):
    template = await db.get(DocumentTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"rendered": _render_template_body(template, request.variables)}


@router.post("/document-templates/{template_id}/generate")
async def generate_document(
    template_id: UUID,
    request: GenerateDocumentRequest,
    db: AsyncSession = Depends(get_db),
):
    template = await db.get(DocumentTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    body = _render_template_body(template, request.variables)

    # Generate PDF using reportlab
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from xml.sax.saxutils import escape as xml_escape

    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
        title=template.name,
    )

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        spaceAfter=6,
    )

    story = []
    # Split on blank lines into paragraphs; preserve single-line breaks inside paragraphs
    for block in body.split("\n\n"):
        block = block.strip("\n")
        if not block:
            story.append(Spacer(1, 10))
            continue
        text = xml_escape(block).replace("\n", "<br/>")
        story.append(Paragraph(text, body_style))

    doc.build(story)
    output.seek(0)

    safe_name = template.name.replace(" ", "_")
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{safe_name}.pdf"'
            )
        },
    )
