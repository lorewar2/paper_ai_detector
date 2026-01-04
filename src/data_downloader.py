# Download files from alex dataset and the using the corrosponding dois download full papers. 
import pyalex
from paperscraper.pdf import save_pdf
#pip install git+https://github.com/titipata/scipdf_parser

DOI_SAVE_PATH = "./data/doi_list.txt"

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
    retrieve_pdf_from_doi(1983)
    return 0

if __name__ == "__main__":  
    main()