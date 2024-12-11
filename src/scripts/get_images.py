import os
import requests
import time
import pandas as pd
from tqdm import tqdm
import json


def normalize_data(metadata_df):
    countries_map = {
    "México":"mexico",
    "Қазақстан":"Kazakhstan",
    "New Zealand / Aotearoa":"new zealand",
    "Føroyar":"faroe islands",
    "Ghana":"ghana",
    "Canada":"canada",
    "پاکستان":"pakistan",
    "Guatemala":"guatemala",
    "Australia":"australia",
    "Botswana":"botswana",
    "Indonesia":"indonesia",
    "Palestinian Territory":"palestine",
    "འབྲུགཡུལ་":"bhutan",
    "Ísland":"iceland",
    "Shqipëria":"albania",
    "Magyarország":"hungary",
    "Česko":"czechia",
    "Uruguay":"uruguay",
    "Беларусь":"belarus",
    "Türkiye":"Turkey",
    "Jersey":"jersey",
    "Nederland":"netherlands",
    "Северна Македонија":"north macedonia",
    "대한민국":"south korea",
    "ישראל":"israel",
    "Slovensko":"slovakia",
    "الأردن":"jordan",
    "Kenya":"kenya",
    "Pilipinas":"philippines",
    "Argentina":"argentina",
    "Schweiz/Suisse/Svizzera/Svizra":"switzerland",
    "臺灣":"taiwan",
    "Eesti":"estonia",
    "Rwanda":"rwanda",
    "Uganda":"uganda",
    "eSwatini":"eswatini",
    "България":"bulgaria",
    "Кыргызстан":"kyrgyzstan",
    "Gibraltar":"gibraltar",
    "France":"france",
    "Costa Rica":"costa rica",
    "Hrvatska":"croatia",
    "Isle of Man":"isle of man",
    "বাংলাদেশ":"bangladesh",
    "België / Belgique / Belgien":"belgium",
    "Bolivia":"bolivia",
    "قطر":"qatar",
    "Sverige":"sweden",
    "Monaco":"monaco",
    "Sénégal":"senegal",
    "Ελλάς":"greece",
    "Россия":"russia",
    "لبنان":"lebanon",
    "Nigeria":"nigeria",
    "Italia":"italy",
    "España":"spain",
    "Lëtzebuerg":"luxembourg",
    "United States":"united states",
    "Lietuva":"lithuania",
    "Sri Lanka":"sri lanka",
    "Malta":"malta",
    "Crna Gora / Црна Гора":"montenegro",
    "ประเทศไทย":"thailand",
    "Suomi / Finland":"finland",
    "Lesotho":"lesotho",
    "South Africa":"south africa",
    "Andorra":"andorra",
    "Panamá":"panama",
    "United Kingdom":"united kingdom",
    "الإمارات العربية المتحدة":"united arab emirates",
    "India":"india",
    "Malaysia":"malaysia",
    "Latvija":"latvia",
    "中国":"china",
    "عمان":"oman",
    "República Dominicana":"dominican republic",
    "Deutschland":"germany",
    "Liechtenstein":"liechtenstein",
    "Éire / Ireland":"ireland",
    "Србија":"serbia",
    "Perú":"peru",
    "Brasil":"brazil",
    "Falkland Islands":"falkland islands",
    "Danmark":"denmark",
    "Madagasikara / Madagascar":"madagascar",
    "Colombia":"colombia",
    "Norge":"norway",
    "Portugal":"portugal",
    "Україна":"ukraine",
    "San Marino":"san marino",
    "Ecuador":"ecuador",
    "مصر":"egypt",
    "تونس":"tunisia",
    "日本":"japan",
    "Slovenija":"slovenia",
    "Singapore":"singapore",
    "ປະເທດລາວ":"laos",
    "Chile":"chile",
    "Polska":"poland",
    "Монгол улс ᠮᠤᠩᠭᠤᠯ ᠤᠯᠤᠰ":"mongolia",
    "România":"romania",
    "Österreich":"Austria" 
    }
    def normalize_country(country):
        if country not in countries_map:
            return 'cambodia'
        else:
            return countries_map[country]
    countries = metadata_df['country'].tolist()
    normalized_countries = [normalize_country(country) for country in countries]
    metadata_df['normalized_country'] = normalized_countries
    return metadata_df



def metadata_to_image(metadata_df):
    IMG_DIR = "GeoClip_data"
    gsv_url = "https://maps.googleapis.com/maps/api/streetview"
    total = len(metadata_df)
    start = 0
    end = len(metadata_df)

    with tqdm(total=end - start, desc="Downloading Images") as pbar:
        for idx, row in metadata_df[start:end].iterrows():
            lat, lng = row['lat'], row['lng']
            country = row['normalized_country']

            country_dir = os.path.join(IMG_DIR, country)
            os.makedirs(country_dir, exist_ok=True)

            for j in range(4):
                heading = j * 90
                pic_params = {
                    "key": "xxx",
                    "location": f"{lat},{lng}",
                    "size": "640x640",
                    "fov": "90",
                    "heading": str(heading),
                    "pitch": "0"
                }
                image_filename = f"{lat}_{lng}_{country}_{j+1}.png"
                image_path = os.path.join(country_dir, image_filename)

                if os.path.exists(image_path):
                    continue
                try:
                    response = requests.get(gsv_url, params=pic_params, timeout=10)
                    response.raise_for_status()
                    with open(image_path, "wb") as img_f:
                        img_f.write(response.content)
                except requests.RequestException as e:
                    print(f"Failed to download image {image_path}: {e}")
                    return
                time.sleep(.1)
            if idx % 100 == 0:
                pbar.update(100)
    print("Finished downloading images")
def get_files_with_extension(directory, extension):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(extension.lower()):
                files.append(os.path.join(root, filename))
    return files

def convert_images_to_json(output_filename):
    files = get_files_with_extension('GeoClip_data', '.png')
    with open(output_filename, 'w') as f:
        written_count = 0
        for image_path in files:
            caption = f"An image representing {image_path.split('/')[1]}"
            line_dict = {'image_path': image_path, "caption": caption}
            json_line = json.dumps(line_dict, indent = None, separators = (",", ':'))
            f.write(json_line + '\n')
            written_count += 1
        print(f"wrote {written_count} lines")

if __name__ == "__main__":
    metadata_df = pd.read_csv('../../data/metadata_og.csv')

    metadata_df = normalize_data(metadata_df)

    metadata_to_image(metadata_df)

    convert_images_to_json('dataset.json')