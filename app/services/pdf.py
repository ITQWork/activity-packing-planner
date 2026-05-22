from fpdf import FPDF
from app.models.models import Trip, TripPackedItem
from typing import List

def generate_pdf(trip: Trip, packed_items: List[TripPackedItem]):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Packing List: {trip.destination}", ln=True, align='C')
    
    # Trip Info
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Dates: {trip.start_date} to {trip.end_date}", ln=True)
    pdf.cell(0, 10, f"Activity: {trip.activity.name if trip.activity else 'N/A'}", ln=True)
    pdf.ln(5)
    
    # Items by category
    categories = {}
    for pi in packed_items:
        # Assuming item_detail (Item model) and category are loaded
        cat_name = "Other"
        if pi.item and pi.item.category:
            cat_name = pi.item.category.name
            
        if cat_name not in categories:
            categories[cat_name] = []
        categories[cat_name].append(pi)
        
    total_weight = 0
    
    for cat_name, items in categories.items():
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, cat_name, ln=True)
        pdf.set_font("Arial", '', 12)
        for pi in items:
            status = "[x]" if pi.is_packed else "[ ]"
            item_name = pi.item.name if pi.item else f"Item {pi.item_id}"
            weight = pi.item.unit_weight * pi.quantity if pi.item else 0
            total_weight += weight
            pdf.cell(0, 10, f"{status} {pi.quantity}x {item_name} ({weight}g)", ln=True)
        pdf.ln(2)
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total Estimated Weight: {total_weight}g", ln=True)
    
    return pdf.output()
