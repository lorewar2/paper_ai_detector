# Download files from alex dataset and the using the corrosponding dois download full papers. 
import pyalex
import os
import random
#from paperscraper.pdf import save_pdf
#pip install git+https://github.com/titipata/scipdf_parser

DOI_SAVE_PATH = "./data/doi_list.txt"
INTERSECT_ID_SAVE_PATH = "./data/intersect_list.txt"

def find_intersecting_authors_2021_2023_2025():
    years_to_analyze = [2021, 2023, 2025]
    # load previous entries
    author_dict = load_dict_from_file(years_to_analyze)
    #print(pyalex.Works().filter(publication_year = year).select("authorships").count())
    pyalex.config.email = "mw8511@live.com"
    # loop through years
    for year in years_to_analyze:
        year_index = int((year - 2021) / 2)
        random_seed_start = random.randint(0, 1_000_000)
        for seed in range(random_seed_start, random_seed_start + 100):
            # seed to get random sample of 10_000 (max value), select only authorships
            pages = pyalex.Works().sample(10_000, seed).filter(publication_year = year, has_oa_accepted_or_published_version = True, language = "en").select("authorships").paginate(method="page", per_page=200)
            page_number = 0
            for page in pages:
                page_number += 1
                print(year, seed, seed -  random_seed_start,  page_number, len(author_dict))
                for work in page:
                    # save in dict, update bool based on year
                    for author in work["authorships"]:
                        if author["author"]["id"] is not None:
                            key = author["author"]["id"].split("/")[-1]
                            if author_dict.get(key) is not None:
                                author_dict[key][year_index] = True
                            else:
                                author_dict[key] = [False, False, False]
                                author_dict[key][year_index] = True
                if page_number == 50:
                    break
            # intermediate save
            if seed % 10 == 0 and seed != 0:
                keys_save = list()
                for key in author_dict.keys():
                    if author_dict[key][year_index] == True:
                        keys_save.append(key + "\n")
                with open("./data/" + str(year) + ".txt", "w") as f:
                    f.writelines(keys_save)

    # analyze the dict
    count_2021 = 0
    count_2023 = 0
    count_2025 = 0
    count_intersect = 0
    keys_intersect = []
    for key in author_dict.keys():
        if author_dict[key][0] == True:
            count_2021 += 1
        if author_dict[key][1] == True:
            count_2023 += 1
        if author_dict[key][2] == True:
            count_2025 += 1
        if author_dict[key][0] and author_dict[key][1] and author_dict[key][2] == True:
            count_intersect += 1
            keys_intersect.append(key + "\n")
    print("2021: ", count_2021, " 2023: ", count_2023, " 2025: ", count_2025, " Intersect: ", count_intersect)
    with open(INTERSECT_ID_SAVE_PATH, "w") as f:
        f.writelines(keys_intersect)
    return

def load_dict_from_file(years_to_analyze):
    author_dict = dict()
    for year in years_to_analyze:
        year_index = int((year - 2021) / 2)
        file_path = "./data/" + str(year) + ".txt"
        if os.path.isfile(file_path):
            # open the file and load up the dict
             with open(file_path, 'r') as file:
                for line in file:
                    key = line.strip()
                    if author_dict.get(key) is not None:
                        author_dict[key][year_index] = True
                    else:
                        author_dict[key] = [False, False, False]
                        author_dict[key][year_index] = True
    return author_dict
# obsolete
def get_and_save_dois():
    # go through years 1980 to 2025
    for year in range(1980, 2026):
        print(year)
        doi_list = list()
        # loop using different seeds until we get the desired amount of data (dois)
        for seed in range(0, 3):
            pages = pyalex.Works().sample(10_000, seed=seed).filter(publication_year=year, is_oa=True).select("doi").paginate(method="page", per_page=200)
            for page in pages:
                for result in page:
                    print(result["doi"])
                    if result["doi"] != None:
                        doi_list.append(result["doi"] + "\n")
        with open(DOI_SAVE_PATH, "a") as f:
            f.write(str(year) + "\n")
            f.writelines(doi_list)
    return

def retrieve_pdf_from_doi(year):
    # go through the doi list and get the releavant doi for the year and make a list
    start = False
    year_doi_list = list()
    with open(DOI_SAVE_PATH, 'r') as file:
        for line in file:
            if line.strip() == str(year + 1):
                break
            if start == True:
                year_doi_list.append(line.strip())
            if line.strip() == str(year):
                start = True
    print(len(year_doi_list))
    # try to download the doi, if fail do nothing if success put the file in year folder and save it to success list
    for doi in year_doi_list:
        name = doi
        print(doi)
        out = "./data/" + str(year) + "/" + name.replace("/", "").replace(":", "") + ".pdf"
        paper_data = {'doi': doi}
        save_pdf(paper_data, filepath=out)
        print(out)
        #scihub_download("https://doi.org/10.1145/3375633", out=out, paper_type="doi")
        break
    return

def main():
    #get_and_save_dois()
    #work = pyalex.Works().filter(doi = "https://doi.org/10.1186/s12859-024-06020-0").get()
    #pages = pyalex.Authors().filter(id = "https://openalex.org/A5060528195").get()
    #count = 0
    #print(pages)
    find_intersecting_authors_2021_2023_2025()
    #retrieve_pdf_from_doi(1983)
    return 0

if __name__ == "__main__":  
    main()