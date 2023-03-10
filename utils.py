# necessary to implement `download_data()` [see below]
import requests
from pathlib import Path
# standard data analysis libraries
import pandas as pd, numpy as np 
# utility imports
import json, re
from IPython.display import *

#########################
# Environment Variables #
#########################

base_url = "https://erowid.org/experiences/research/"
api_code = "exp_api.php?api_code=berkeley_bcsp_tyrone_2022"
lnk = base_url + api_code
to_collect = {
               "Cannabis" : [1], 
               "LSD" : [2], 
               "MDMA" : [3], 
               "Ketamine" : [31],
               "Psilocybin/Mushrooms" : [39, 66, 239],
               "DMT" : [18],
               "Mescaline/Cacti/Children" : [36, 809, 543, 826]
            }

####################
# Erowid Utilities #
####################

def getData(conditions, fileName):
    results = {}
    for name, ids in to_collect.items():
        records = [{k : eval(v.toJSON().replace("null", "'null'")) 
                    for k,v in getExperiences(num, int(10e10),
                        ['isPure'] + conditions).items()}
                for num in ids]
        results[name] = sumDict(records)
    writeDict(results, fileName)
    Experience.toFrame(results).to_csv(f"csv/{fileName}.csv", index=False)
    return results

def getExperiences(subID, most=20, conditions=None):
    add =  "&a=experience_data" + \
          f"&substance_id={subID}&max={most}" + \
           "&format=xml"
    url = lnk + add 
    content = requests.get(url).text
    exps = re.split(r"<experience>|</experience>", content)[1:-1]
    while ("\n\n\n" in exps):
        exps.remove("\n\n\n")
    dct = {}
    for i in range(len(exps)):
        exp = Experience(exps[i])
        fits = True
        if conditions:
            for condition in conditions:
                met = eval(f"exp.{condition}()")
                fits = fits and met
        if fits:
            dct[exp.get("id")] = exp
    return dct

def experienceList(subID, most=20, conditions = None):
    dct = getExperiences(subID, most=most, conditions = conditions)
    return list(dct.values())

def retrieve(
    subID : int,
    most : int = 20, 
    conditions : list = None):
    """
    Add substances to ``dictionaries/retrieved.json``
    that meet all conditions in ``conditions``,
    and update the file accordingly

    Parameters
    ----------
    subID : int
        The numerical ID of the substance to 
        get experiences from.
    most : int = 20
        The maximum amount of experiences to pull;
        this is the number of all experiences, the 
        number which meet ``conditions`` may be much
        lower.
    conditions : list = None
        Conditions that each experience must meet in
        order to be part of the returned dictionary.

    Returns
    -------
    Updated Dictionary : dict
    """
    dct = getExperiences(subID, most, conditions)
    retrieved = readDict("retrieved")
    working = retrieved[subID]
    for k, v in dct.items():
        if not (k in working.keys()):
            working[k] = vars(v)
    retrieved[subID] = working
    writeDict(retrieved, "retrieved")

########################
# Dictionary Utilities #
########################

def intKey(dct : dict):
    """Index a fiven dictionary recursively"""
    if (type(dct) != dict) or (dct == {}):
        return dct
    try:
        return {int(k) : intKey(v) for k, v in dct.items()}
    except Exception as e:
        return dct
    
def readDict(file : str):
    """
    Reads in a json file from the dictionaries directory into a python dictionary and returns it
    """
    with open(f"dictionaries/{file}.json") as infile:
        subs = json.load(infile)
    return intKey(subs)

def sumDict(dicts : list or dict):
    """Merge multiple dictionaries"""
    full = {}
    for dic in dicts:
        full = full | dic
    return full

def writeDict(dct : dict, file : str):
    """Write a python dictionary to a .json file"""
    with open(f"dictionaries/{file}.json", "w") as outfile:
        json.dump(dct, outfile, indent=4, sort_keys=True)
    return dct

def addDict(file = None, dct = None, keys = None, values = None):
    if not dct: 
        dct = readDict(file)
    if keys and values:
        if type(keys) != list:
            dct[keys] += values
        else:
            assert len(keys) == len(values), \
            f"""Keys and values must have same length:
                Given Keys:{len(keys)} and Values:{len(values)}"""
            for key, value in zip(keys, values):
                dct[key] += value  
    writeDict(dct, file)
    
def reduceDict(dct):
    new_dct = {}
    if dct == bad:
        trip_type = "bad"
    elif dct == first:
        trip_type = "first"
    elif dct == general:
        trip_type = "general"
    for substance, subDict in dct.items():
        for id, ssDict in subDict.items():
            info = ssDict['info']
            info["substance"] = substance
            info["trip_type"] = trip_type
            new_dct[id] = info
    return new_dct

def dict_to_csv(dct):
    experiences = pd.DataFrame.from_dict(dct, orient='index').reset_index(drop = True)
    keep = ["id", "trip_type", "substance", "substance-string", 
        "substance-id-list", "submitted-date", "published-rating", 
        'primary-category-id', 'list-number', 'intensity',
        'category-id-list', 'experience-year', 'gender', 
        "author", "title", "text"]
    mapper = {"id": "id", 
            "trip_type": "trip_type", 
            "substance": "substance", 
            "substance-string": "substance_name", 
            "substance-id-list": "substance_id", 
            "submitted-date": "date", 
            "published-rating": "rating",
            "primary-category-id": 'category_id', 
            'list-number': 'list_number', 
            'intensity': 'intensity'}
    return experiences[keep].rename(columns = mapper)

#####################
# General Utilities #
#####################

def download_data(url, file):
    """Download data from url to file"""
    file_path = Path(file)
    print('Downloading...', end=' ')
    resp = requests.get(url)
    with file_path.open('wb') as f:
        f.write(resp.content)
    print('Done!')
    return file_path

def show(*args, tags = []):
    """
    Display text or other data using Ipython
    
    Parameters
    ––––––––––
    x : str | default ``None``
        the value(s) to display, if None,
        two empty lines are displayed
        
    tags : list of str | default ``[]``
        uses each element of tags as an HTML
        tag; tags will be applied from left
        to right, so the last tage in the 
        list will be the outermost applied
    
    Returns
    –––––––
    None
    """
    assert (tags == []) or (type(tags[0]) == str), "tags must contain strings"
    for i in args:
        if type(i) != str:
            i = str(i)
        for tag in tags:
            i = f"<{tag}>{i}</{tag}>"
        display(Markdown(i))

def flatten(lists):
    """Flatten multiple lists"""
    return sum([[lst] if type(lst) != list else lst for lst in lists], [])

####################
# Experience Class #
####################

class Experience:
    
    def __repr__(self):
        dct  = self.info
        ss, ln = dct["substance-string"].strip(), dct["list-number"]
        return f"Experience: {{ Substance: {ss},  List-ID: {ln} }}"
        
    def __str__(self):
        return self.name
        
    def __init__(self, string : str, 
                 info = None, text = None, name = None):
        self.string = string
        self.readInfo()
        for i, k in self.info.items():
            if self.info.get(i) == "":
                self.info[i] = None
        self.makeName()
    
    def fromDict(dct : dict):
        return Experience(**dct)

    def fromFrame(frame : str):
        return pd.read_csv(f"csv/{frame}.csv")
    
    def toFrame(c : dict):
        exps = {key : { k : Experience(**v) for k, v in val.items()} for key, val in c.items()}
        dl = []
        for key in exps.keys():
            for exp in exps[key].values():
                temp = exp.info
                temp["substance"] = key
                temp["name"] = exp.name
                dl.append(temp)
        frame = pd.DataFrame(dl)
        reordered = ["substance", "name", "id", "list-number", "title", "author", 
                    "substance-string", 'body-weight', 'gender', 'published-date', 'submitted-date',
                    'experience-year', 'intensity', 'primary-category-id', 'substance-id-list', 
                    'category-id-list', 'published-rating', 'body-changes', 'text']
        frame = frame[reordered]
        frame.columns = ["category", "name", "id", "list index", "title", "author", 
                        "substance", 'weight', 'gender', 'published', 'submitted',
                        'year', 'intensity', 'primary category', 'substance id', 
                        'secondary category', 'rating', 'changes', 'text']
        frame["word count"] = frame["text"].str.rsplit().apply(len)
        return frame
    
    def get(self, key : str):
        if key in (inf := self.info):
            return inf.get(key)
        else:
            print(f"{key} is not a valid key.",
                  "Please select one of the following: \n")
            for key in inf.keys():
                if key == "text":
                    print(key)
                else:
                    print(key, end = "," + " "*(30 - len(key)) + "\t")
                    
    def isPure(self):
        tpe = (type(self.get("substance-id-list")) == int)
        nme = self.get("substance-string")
        mul = not (("," in nme) or ("&" in nme))
        return tpe and mul
    
    def isFirst(self):
        return 2 in self.get("category-id-list")
    
    def isBad(self):
        return 6 in self.get("category-id-list")
    
    def isGeneral(self):
        return 1 in self.get("category-id-list")
        
    def readInfo(self):
        vallst = re.findall(r"<(.*)>(.*)</.*>", self.string)
        dct = dict(vallst)
        for key in dct.keys():
            try:
                dct[key] = eval(dct[key])
            except Exception as e:
                dct[key] = dct[key]
        self.info = dct
        txt = re.split(r"<experience-text>|</experience-text>", self.string)[1]
        self.info['text'] = txt
        self.text = txt
        self.info["list-number"] = self.info["list-number"] - 1
        
    def makeName(self):
        dct = self.info
        name = dct["substance-string"].strip() + str(dct["list-number"])
        self.name = name.lower().replace(" ", "_").replace("&", "n")
        
    def listInfo(self):
        return list(self.info.keys())

    def toJSON(self):
        raw = json.dumps(self, 
                         default= lambda o: vars(o), 
            sort_keys=True, indent=4)
        return raw
    
    def writeToFile(title, text):
        with open(f"narratives/txt/{title}.txt", "w") as f:
            f.write(text)
        
####################
# Setup Functions  #
####################

bad, first, general = [readDict(f"data/{name}") for name in ["bad", "first", "general"]]