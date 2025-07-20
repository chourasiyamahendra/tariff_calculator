import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# Configure Streamlit page
st.set_page_config(page_title="Electricity Cost to Consumer", page_icon="⚡")

# Paths
logo_path = "logo.png"  # Make sure logo.png is in the same directory
db_file = "database.xlsx"  # Adjust path if needed

# Header: Logo and Date
header_col1, header_col2 = st.columns([6, 1])
with header_col1:
    st.markdown("<h1 style='font-size:28px;'>Electricity Cost to Consumer</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:20px;'>Delivered cost of electricity including all applicable charges</h3>", unsafe_allow_html=True)
with header_col2:
    if os.path.exists(logo_path):
        st.image(logo_path, width=80)
    st.markdown(f"<p style='font-size:14px;text-align:right;'>{datetime.now().strftime('%d-%m-%Y')}</p>", unsafe_allow_html=True)

# Consumer details
consumer_name = st.text_input("👤 Consumer Name")
consumer_number = st.text_input("🔢 Consumer Number")

# Load database
if not os.path.exists(db_file):
    st.error(f"Database file '{db_file}' not found!")
else:
    df = pd.read_excel(db_file)

    # User Inputs
    connection_type = st.selectbox("Select Connection Type", [""] + list(df["Connection Type"].unique()))
    subcategory = st.selectbox("Select Sub Category", [""] + (list(df[df["Connection Type"] == connection_type]["Sub Category"].unique()) if connection_type else []))
    fac = st.number_input("Enter FAC (Rs./Unit):", min_value=0.0, step=0.01)
    tax_on_sale = st.number_input("Enter Tax on Sale (Rs./Unit):", min_value=0.0, step=0.01)
    electricity_duty = st.number_input("Enter Electricity Duty (%):", min_value=0.0, step=0.01)

    total_cost = None

    # Centered buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("Calculate Landed Cost"):
            if connection_type and subcategory:
                row = df[(df["Connection Type"] == connection_type) & (df["Sub Category"] == subcategory)]
                if not row.empty:
                    energy_charges = row.iloc[0]["Energy Charges (Rs./kWh)"]
                    wheeling_charges = row.iloc[0]["Wheeling Charges (Rs./kWh)"]
                    ed_factor = (energy_charges + wheeling_charges + fac) * (electricity_duty / 100)
                    total_cost = round(energy_charges + wheeling_charges + fac + tax_on_sale + ed_factor, 2)

                    # Proper formatted output with DARK GREEN background
                    st.markdown(f"""
                        <div style='background-color:#155724;color:white;padding:10px;border-radius:8px;'>
                        <p>💡 <b>Energy Charges (Rs./Unit):</b> {energy_charges:.2f}</p>
                        <p>⚙️ <b>FAC (Rs./Unit):</b> {fac:.2f}</p>
                        <p>💸 <b>Tax on Sale (Rs./Unit):</b> {tax_on_sale:.2f}</p>
                        <p>📊 <b>Electricity Duty (%):</b> {electricity_duty:.2f}</p>
                        <hr>
                        <p style='font-size:18px;'>✅ <b>Landed Cost of Electricity (Rs./Unit):</b> {total_cost:.2f}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # PDF generation function
                    def create_pdf():
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)

                        # Header
                        if os.path.exists(logo_path):
                            pdf.image(logo_path, x=160, y=10, w=40)
                        pdf.ln(20)
                        pdf.set_font("Arial", size=16)
                        pdf.cell(0, 10, "Electricity Cost to Consumer", ln=True, align="C")
                        pdf.set_font("Arial", size=12)
                        pdf.cell(0, 10, "Delivered cost of electricity including all applicable charges", ln=True, align="C")
                        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d-%m-%Y')}", ln=True, align="C")
                        pdf.ln(10)

                        # Table Data
                        pdf.set_fill_color(240, 240, 240)
                        table_data = [
                            ("Consumer Name", consumer_name),
                            ("Consumer Number", consumer_number),
                            ("Connection Type", connection_type),
                            ("Sub Category", subcategory),
                            ("Energy Charges (Rs./Unit)", f"{energy_charges:.2f}"),
                            ("FAC (Rs./Unit)", f"{fac:.2f}"),
                            ("Tax on Sale (Rs./Unit)", f"{tax_on_sale:.2f}"),
                            ("Electricity Duty (%)", f"{electricity_duty:.2f}"),
                            ("Landed Cost (Rs./Unit)", f"{total_cost:.2f}")
                        ]

                        col_width = pdf.w / 2.2
                        for param, value in table_data:
                            pdf.cell(col_width, 10, param, border=1, align="L", fill=True)
                            pdf.cell(col_width, 10, str(value), border=1, align="L", fill=True)
                            pdf.ln()

                        # Footer - Personal info
                        pdf.ln(15)
                        pdf.set_text_color(50, 50, 50)
                        pdf.set_font("Arial", size=10)
                        footer_text = (
                            "Mahendra Chourasiya | Project Manager & Solar Implementation Specialist\n"
                            "Gram Oorja Solutions Private Limited\n"
                            "+91-9689865168 | mahendra@gramoorja.in"
                        )
                        pdf.multi_cell(0, 8, footer_text, align="C")

                        # Return PDF as bytes
                        pdf_output = pdf.output(dest="S").encode("latin-1")
                        return pdf_output

                    # Download Button
                    with col_btn2:
                        pdf_bytes = create_pdf()
                        st.download_button(
                            "📄 Download Report",
                            data=pdf_bytes,
                            file_name="Electricity_Cost_Report.pdf",
                            mime="application/pdf"
                        )

                else:
                    st.error("No matching record found.")
            else:
                st.warning("⚠️ Please select both Connection Type and Sub Category.")

    # Footer for Streamlit page
    st.markdown("""
        <hr style="border:1px solid #bbb">
        <div style="text-align:center; color:gray;">
            👤 <b>Mahendra Chourasiya</b> | 💼 Project Manager & Solar Implementation Specialist <br>
            🏢 Gram Oorja Solutions Private Limited <br>
            📞 +91-9689865168 | ✉️ <a href="mailto:mahendra@gramoorja.in" style="color:blue;">mahendra@gramoorja.in</a>
        </div>
    """, unsafe_allow_html=True)
