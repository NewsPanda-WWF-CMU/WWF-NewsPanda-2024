from fpdf import FPDF

# Creating an instance of FPDF class
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Adding a title to the PDF
pdf.multi_cell(0, 10, "Summary Report on Recent Proposals and Related News Articles", align='C')

# List of proposals and their related articles
proposals = [
    {
        "title": "1. Diversion of Forest Land in Kondapak RF, Siddipet, Telangana",
        "proposal_id": "FP/TG/ROAD/156948/2022",
        "proposal_date": "31-12-2022 15:20:58",
        "articles": [
            "Telangana ranking second in diverting forest land despite green initiatives (Deccan Chronicle). Link: https://www.deccanchronicle.com/nation/current-affairs/020319/telangana-2nd-in-diverting-forest-land-andhra-pradesh-stands-6th.html",
            "Nationwide trend of forest land diversion for development projects (DownToEarth). Link: https://www.downtoearth.org.in/news/forests/india-continues-to-lose-forest-land-to-non-forestry-projects-66626",
            "Wildlife sightings in Kondapak Reserve Forest, highlighting environmental impact (Telangana Today). Link: https://telanganatoday.com/leopards-on-prowl-near-mallanna-sagar-project-in-siddipet"
        ]
    },
    {
        "title": "2. Kathpatiya-Gudauli to Daula Motor Road, Uttarakhand",
        "proposal_id": "FP/UK/ROAD/33229/2018",
        "proposal_date": "31-12-2022 00:00:00",
        "articles": [
            "Road projects in Uttarakhand enhancing tourism and employment (The New Indian Express). Link: https://www.newindianexpress.com/nation/2022/jan/04/roads-being-built-in-uttarakhand-will-open-its-doors-to-prosperity-union-minister-nitin-gadkari-2400300.html",
            "Discussion of various road projects in Uttarakhand, including the proposed road (Garhwal Post). Link: https://garhwalpost.in/all-proposals-of-ukhand-govt-regarding-roads-will-be-approved-soon-gadkari/",
            "Broader overview of infrastructure development in Uttarakhand (Elets eGov). Link: https://egov.eletsonline.com/2022/06/uttarakhand-leading-the-road-to-transformation-in-india/"
        ]
    },
    {
        "title": "3. Road from L054-L034 to Garhisankh, Jharkhand",
        "proposal_id": "FP/JH/ROAD/138521/2021",
        "proposal_date": "31-12-2021 16:53:47",
        "articles": [
            "Local tribals refusing road construction to preserve jungles (The New Indian Express). Link: https://www.newindianexpress.com/nation/2021/mar/07/in-love-with-jungles-jkhand-tribals-refuse-road-work-2273461.html"
        ]
    },
    {
        "title": "4. Adani Hazira Port, Gujarat",
        "proposal_id": "FP/GJ/Others/22337/2016",
        "proposal_date": "31-12-2021 13:09:29",
        "articles": [
            "Expansion plans for new berths and increased cargo capacity (Maritime Gateway). Link: https://www.maritimegateway.com/adani-plans-expansion-of-hazira-port/",
            "Controversy over extra charges proposed by the port (ET Infra). Link: https://infra.economictimes.indiatimes.com/news/ports-shipping/adani-hazira-port-trade-set-for-a-face-off-over-extra-charges/93690792",
            "Significant investment for the expansion of port facilities (DST - Daily Shipping Times). Link: https://dst.news/adani-hazira-port-to-invest-rs-19000-cr-to-expand-at-least-6-times-to-its-present-size-sources/"
        ]
    }
]

for proposal in proposals:
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, proposal["title"])
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, f"Proposal ID: {proposal['proposal_id']}")
    pdf.multi_cell(0, 10, f"Proposal Date: {proposal['proposal_date']}")

    # Add the articles related to the proposal
    for article in proposal["articles"]:
        pdf.set_font("Arial", 'I', 10)
        pdf.multi_cell(0, 10, article)

    # Add a separator for readability
    pdf.cell(0, 10, "", 0, 1)

# Saving the PDF
pdf.output("Proposals_Summary_Report.pdf")
