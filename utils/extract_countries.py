import pycountry
import pandas as pd

def extract_countries(affiliations):
    if pd.isna(affiliations):
        return None

    countries_info = {country.name for country in pycountry.countries}  # Use a set for faster lookup
    additional_mappings = {
        "USA": "United States",
        "U.K.": "United Kingdom",
        "U.S.": "United States",
        "South Korea": "South Korea",
        "Taiwan": "Taiwan, Province of China",
        "Turkey": "Turkey",
        "Iran": "Iran",
        "Palestine": "Palestine",
        "Tehran": "Iran",
        "Ankara": "Turkey",
        "Istanbul": "Turkey",
        "Izmir": "Turkey",
        "Denizli": "Turkey",
        "Trabzon": "Turkey",
        "Eskişehir": "Turkey",
        "Kocaeli": "Turkey",
        "Antalya": "Turkey",
        "Muğla": "Turkey",
        "Gazi University": "Turkey",
        "Kadir Has University": "Turkey",
        "Yaşar University": "Turkey",
        "Ozyegin University": "Turkey",
        "Michigan State University": "United States",
        "Ryerson University": "Canada",
        "University of Alberta": "Canada",
        "Nitte Meenakshi Institute of Technology": "India",
        "SSN College of Engineering": "India",
        "Czech Republic": "Czech Republic",
        "Amazon": "United States",
        "Origin Energy": "Australia",
        "Fondazione Bruno Kessler": "Italy",
        "Red Tree Consulting": "United States",
        "FACT Inc": "United States",
        "Kennesaw State University": "United States",
        "Marquette University": "United States",
        "Teknobuilt Ltd": "India",
        "Symbiosis International": "India",
        "Nokia Bell Labs": "United States",
        "C Spire": "United States",
        "Cognizant Worldwide Ltd": "United States",
        "University of Southampton": "United Kingdom",
        "ARM Ltd": "United Kingdom",
        "Tenstorrent": "United Kingdom",
        "The Nelson Mandela African Institution of Science and Technology": "Tanzania",
        "National University of Sciences and Technology (NUST)": "Pakistan",
        "Vels Institute of Science Technology and Advanced Studies": "India",
        "Purdue University": "United States",
        "Zhejiang University": "China",
        "Princeton University": "United States",
        "Ericsson Research": "Sweden",  # Assuming the primary location, might need specific info if different
        "University of Washington Tacoma": "United States",
        "Iowa State University": "United States",
        "University of Milan": "Italy",
        "IBM T.J. Watson Research Center": "United States",
        "University of Florida": "United States",
        "Peking University": "China",
        "Oakland University": "United States",
        "National Institute of Information and Communications Technology": "Japan"
    }

    # Split the affiliation string by commas to check individual components
    parts = affiliations.split(';')
    detected_countries = set()

    for part in parts:
        # Check direct full name matches and common abbreviations
        for country in countries_info:
            if country in part:
                detected_countries.add(country)
                break  # Stop checking after the first match to prevent double counting
        else:
            # Check additional mappings if no direct match is found
            for abbr, full_name in additional_mappings.items():
                if abbr.lower() in part.lower():
                    detected_countries.add(full_name)
                    break

    if not detected_countries:
        print(f"Unable to extract country from: {affiliations}")
        return None

    return list(detected_countries)