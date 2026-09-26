"""Expand the Bengaluru locality options used by property listings."""

from collections.abc import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260926_55"
down_revision: str | None = "20260926_54"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


LOCALITIES = """
Electronic City Phase I
Bannerghatta Road
Doddenakundi
Kanakapura Road
Indira Nagar
K R Puram
Thanisandra Main Road
Hennur Road
Horamavu
Hosur Road
Panathur
Electronic City Phase II
Kundalahalli
Marathahalli-Sarjapur Outer Ring Road
Kaggadasapura
CV Raman Nagar
Hosa Road
Old Airport Road
Old Madras Road
Budigere
Hoodi
Off Sarjapur Road
Sarjapur
Harlur
Rajaji Nagar
Bommanahalli
Haralur Road
Kadugodi
HBR Layout
Raja Rajeshwari Nagar
Kasturi Nagar
Yeshwanthpur
Domlur
Kalyan Nagar
Thubarahalli
RT Nagar
Banaswadi
Begur Road
Kasavanahalli
Bilekahalli
Chandapura
Yelahanka New Town
Vidyaranyapura
AECS Layout
Devanahalli
Ulsoor
Chandapura Anekal Road
Kadubeesanahalli
Begur
Marathahalli ORR
Doddaballapur Road
Jalahalli West
Mysore Road
Sahakara Nagar
Jakkur
Bellandur Outer Ring Road
Basaveshwara Nagar
Murugeshpalya
HSR Layout Sector 2
Munnekollal
JP Nagar Phase 8
JP Nagar Phase 7
Tumkur Road
Ejipura
Singasandra
Mathikere
Kudlu Gate
Hoskote
Jigani
Sarjapur Attibele Road
Kaikondrahalli
Arekere
HSR Layout Sector 1
TC Palya Road
Whitefield Road
Shigehalli
ITPL Road
Kammanahalli
New Thippasandra
HRBR Layout
Kodigehalli
Chansandra
Kengeri
Gunjur
Nagavara
Babusa Palya
Hulimavu
Tavarekere-BTM
Wilson Garden
Frazer Town
HSR Layout Sector 3
HSR Layout Sector 7
JP Nagar Phase 5
Outer Ring Road
JP Nagar Phase 6
Nelamangala
Vishweshwaraiah Layout
Richmond Town
Bommasandra
Banashankari 3rd Stage
BEML Layout
MS Palya
Kodihalli
Pai Layout
Gottigere
Cooke Town
Kumaraswamy Layout
Seegehalli
GM Palya
Devarachikkanahalli
Malleshpalya
Magadi Road
Attibele
Anjanapura
Kalkere
Kengeri Satellite Town
Vignana Nagar
Padmanabha Nagar
RMV 2nd Stage
Cox Town
B Narayanapura
Akshayanagar
Victoria Layout
Kodichikkanahalli
Basavanagar
Dommasandra
Varthur Road
Lingarajapuram
Mahalakshmi Layout
Silk Board
JP Nagar Phase 9
Nagondanahalli
Anekal
Yemalur
Hebbal Kempapura
Kothanur
JP Nagar Phase 1
Bagaluru
Shanthi Nagar
Basapura
Maruthi Sevanagar
Doddakannalli
HAL Layout
JP Nagar Phase 2
Horamavu Agara
OMBR Layout
Aavalahalli
Bannerghatta
Vasanth Nagar
Battarahalli
Kudlu
Kathriguppe
Thavarekere-Magadi Road
Bhoganhalli
Jeevanbheema Nagar
Hanumantha Nagar
Hegde Nagar
Amrutha Halli
MG Road
Devanahalli Road
IVC Road
Margondanahalli
Dasarahalli Hebbal
Srinivasa Nagar
Kaval Byrasandra
Abbigere
Kanaka Nagar
Rachenahalli
Adugodi
Chandra Layout
LB Shastri Nagar
Chikka Banaswadi
Bennigana Halli
New BEL Road
Belathur
Girinagar
Ganga Nagar
Hoskote Malur Road
Sarjapur Bagalur Road
Kogilu
Hongasandra
International Airport Road
Konanakunte
Doddathoguru
Wind Tunnel Road
Panduranga Nagar
Chinnapanna Halli
Shivaji Nagar
ISRO Layout
Madiwala
Siddapura
Peenya
Chamarajpet
Sadashiva Nagar
Nandini Layout
Bellary Road
Mico Layout
Vijaya Bank Colony
HSR Layout Sector 5
Seshadripuram
Ananth Nagar
Richmond Road
Garvebhavi Palya
Immadihalli
Srinagar
Sompura
Jakkasandra
Chikkalasandra
Jayamahal
Dollars Colony
Kempapura
Dodda Banasvadi
Nandi Hills
Choodasandra
Majestic
Cambridge Layout
Kammasandra
Hesaraghatta
Roopena Agrahara
Rajanukunte
Jakkuru Layout
RMV Extension
T Dasarahalli
HSR Layout Sector 6
JP Nagar Phase 4
HAL Layout2
Lavelle Road
Maruthi Nagar
Budigere Road
Nagasandra
Ramagondanahalli
Chikbanavara
Infantry Road
Jalahalli Cross
Byrathi
Jagadish Nagar
Hosakerehalli
Subramanyapura
Neeladri Nagar
Sampangi Rama Nagar
NRI Layout
Rayasandra
Laggere
Srirampura
Venkatapura
R.K. Hegde Nagar
Langford Town
Viveka Nagar
Uttarahalli Main Road
Chelekare
Neelasandra
JP Nagar Phase 3
HSR Layout Sector 4
Jagajeevanram Nagar
RMV
BEML Layout Raja Rajeshwari Nagar
Carmelaram
Kartik Nagar
Mallathahalli
Hosapalaya
Thippasandra
Bagepalli
Cunningham Road
Doddabommasandra
Ullal
Dasarahalli Main Road
Vinayaka Layout
Vasanthapura
Sudhama Nagar
Richards Town
Jalahalli East
Kodathi
Doddaballapur
Gattahalli
Balagere
Kamaksipalya
Chikka Tirupathi
Doddakallasandra
Commercial Street
Bidadi
Banashankari 5th Stage
Kadugondanahalli
Andrahalli
Bagalakunte
Chikkaballapur
Lal Bagh
Gauribidanur
Nagarbhavi Circle
Annapurneshwari Nagar
Gandhi Nagar
Ashok Nagar
Soukya Road
Vittal Mallya Road
Yelachena Halli
Bhuvaneshwari Nagar
Kamanahalli
Teacher's Colony
St. Johns Road
Cholanayakanahalli
Nagadevanahalli
Bidrahalli
Bikasipura
Jangamakote
Sunkadakatte
Chikkajala
Devinagar
Nayanda Halli
Kalena Agrahara
Malur-Hosur Road
Kadabagere
Guttahalli
Attiguppe
Bhoopasandra
Bannerghatta Jigani Road
Sadduguntepalya
Huskur
Thurahalli
Nallurhalli
HMT Layout
Kacharakanahalli
Bileshivale
Maruthi Nagar (Yelahanka)
Shettihalli
Haragadde
K Channasandra
Kannamangala
Byatarayanapura
Talaghattapura
Boyalahalli
Hombegowda Nagar
Rajiv Gandhi Nagar
Kamala Nagar
Doddakammanahalli
Kempegowda Nagar
Attibele - Anekal Road
Kanakapura
Gubalala
Medihalli
Kithiganur
Brigade Road
Jnana Ganga Nagar
Chikkabellandur
Koralur
Kattigenahalli
Dodda Aalada Mara Road
Chikkabidarakallu
Silver Springs Layout
Kaggalipura
Dooravani Nagar
Palace Road
Prashanth Nagar
Nobo Nagar
Kodigehalli - KR Puram
SMV Layout
Suryanagar
Kumbalgodu
Bommenahalli
Munireddy Layout
Chikkathoguru
Baiyyappanahalli
Virupakshapura
Raghavendra Colony
Shankarapura
Jaya Chamarajendra Nagar
Chinnapa Garden
Garudachar Palya
Wheeler Road
Narasapura
Ramohalli
Harohalli
Kolar Road
Anagalapura
Chokkanahalli
Gunjur Mugalur Road
Arasanakunte
Bettahalasur
Chikkakannalli
Kallumantapa
Kothanoor
Sampigehalli
Tilak Nagar
Dayananda Nagar
Bhovi Palya
Chikka Tirupathi Road
Soundarya Layout
Vittal Nagar
Ragavendra Nagar
Sonnenahalli
Chickpet
Haudin Road
Millers Road
Yelanahalli
Defence Colony - Bagalagunte
Race Course Road
Langford Road
Chintamani
Kuthaganahalli
Tharabanahalli
Shanthala Nagar
Chikkagubbi
Pattandur Agrahara
Koppa
Gollahalli
Binny Pete
Kodipur
Lake City
Munireddypalya
Azad Nagar
Rest House Road
Richard's Park
Cottonpete
Dodsworth Layout
Ashirvad Colony
Doddabele
Craig Park Layout
Nelamangala - Chikkaballapura Road
Vaderahalli
Basavanna Nagar
Huttanahalli
Vijaypura
Donnenahalli
Chadalapura
Meenakunte
Lingadheeranahalli
Residency Road
Sidlaghatta
Dabaspete
Kalasipalayam
Somashetti Halli
Chikkanahalli
Kolar-Chikkaballapur Road
Singanahalli
Karuna Nagar
Belatur
Chamundi Nagar
Garden Layout
Sankey Road
Tippenahalli
Bhaktharahalli
Nehru Nagar
Venkateshpuram
Bapuji Nagar
Williams Town
Kammasandra Agrahara
Bikkanahalli
National Highway 207
Kadusonnappanahalli
Solur
Chikkaballapur-Gauribidanur Road
Doddenahalli
Weavers Colony
Hancharahalli
Devasthanagalu
Chikkabasavanapura
Nanjappa Garden
Budihal
Seenappa Layout
CQAL Layout
Shanthi Pura
Lakshmamma Layout
Madhava Nagar
Adakamaranahalli
Vehloli
Hullahalli
Tharaballi
Ganapathihalli
Ballur
Venkatagiri Kote
Kunigal Road
Essel Gardens
S.Medihalli
Koti Hosahalli
Kommaghatta
""".splitlines()


def _normalized(value: str) -> str:
    return "-".join(value.lower().replace(".", "").replace("'", "").split())


def upgrade() -> None:
    bind = op.get_bind()
    existing = {
        row[0]
        for row in bind.execute(
            sa.text("SELECT normalized_name FROM locations WHERE city_name = 'Bengaluru'")
        )
    }
    locations = sa.table(
        "locations",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("parent_id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("location_type", sa.String()),
        sa.column("normalized_name", sa.String()),
        sa.column("city_name", sa.String()),
        sa.column("is_active", sa.Boolean()),
    )
    rows = []
    seen = set(existing)
    for raw_name in LOCALITIES:
        name = raw_name.strip()
        normalized = _normalized(name)
        if not name or normalized in seen:
            continue
        seen.add(normalized)
        rows.append({
            "id": uuid4(),
            "parent_id": None,
            "name": name,
            "slug": normalized,
            "location_type": "LOCALITY",
            "normalized_name": normalized,
            "city_name": "Bengaluru",
            "is_active": True,
        })
    if rows:
        op.bulk_insert(locations, rows)


def downgrade() -> None:
    names = [_normalized(name.strip()) for name in LOCALITIES if name.strip()]
    op.execute(
        sa.text(
            "DELETE FROM locations WHERE location_type = 'LOCALITY' "
            "AND city_name = 'Bengaluru' AND parent_id IS NULL "
            "AND normalized_name IN :names"
        ).bindparams(sa.bindparam("names", expanding=True)).params(names=names)
    )