#necessary to implement `download_data()` [see below]
import requests
from pathlib import Path
import time
#standard data analysis libraries
import numpy as np 
import pandas as pd 
#imports for displaying, rendering, and saving plots and visualizations
import plotly
import plotly.express as px
from IPython.display import *
import plotly.io as pio
import ipywidgets as widgets
from ipywidgets import *
import ast

def writeDict(plots):
    with open('plots.txt','w') as data: 
        data.write(str(plots))

def readDict():
    with open('plots.txt', 'r') as f:
        s = f.read().replace("nan", "None")
        return eval(s)
    
def download_data(data_url, 
                  file):
    file_path = Path(file)
    print('Downloading...', end=' ')
    resp = requests.get(data_url)
    with file_path.open('wb') as f:
        f.write(resp.content)
    print('Done!')
    return file_path

def show_data(height = 700, mode="plain"):
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-" \
        + "1vQJ0Asb2UuESYvMdLE3Td3vh1cMCblbLQbGb0vYw8z0AXQBiQc" \
        + "_GeIkwsu6oJaRTf81wH6bssEefz64/pubhtml?headers=false"
    if mode == "pretty":
        url = "https://docs.google.com/spreadsheets/d/1gSFTniAG3Grj4EZLbmcv21sNnyIJRDkuwoNVumVgxgc"
    return IFrame(url, width = "100%", height = height)

download_data("https://tinyurl.com/bffs-workshop-data", "Workshop Eval.xlsx")

tables = pd.read_excel('Workshop Eval.xlsx', sheet_name = ["Eating on a Budget",
                                                           "Moving Out of the Dorms", 
                                                           "Spending Plan"])
for key in tables.keys():
    tables[key] = tables[key].dropna(subset = tables[key].columns[:-1])
food_labels = ["I follow my grocery budget", 
               "More likely to budget for grocceries", 
               "I can get food", "Feedback"]

house_labels = ["I get how housing affects aid", 
                "I follow my budget",              
                "I will make a budget",         
                "I know where to get food", 
                "I can balance the costs of basic needs",
                "I can chose the best housing for me", "Feedback"]

budget_labels = ["I will make a spending plan", 
                 "I've started saving", 
                 "What's in a spending plan?", 
                 "I have reduced flexible expenses", 
                 "I can manage my finances", "Feedback"]
for key, labels in zip(tables.keys(), [food_labels, house_labels, budget_labels]):
    tables[key].columns = labels

def show(*args, tags = []):
    """
    Display text or other data using Ipython
    
    Parameters
    ––––––––––
    x : str | default ``None``
        the value to display, if None,
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
    
def showtable(self, 
         allrows: bool = False, 
         columns: list = ["all"], 
         rows: int = 20, 
         start: int = 0,
         title: str = None,
         desc: bool = True):
        """
        Display pandas.DataFrame using custom values 

        Parameters
        ––––––––––
        allrows : bool | default ``False``
            Wether or not to show all rows
            
        columns : list | default ``["all"]``
            Default shows all columns. Set to list of 
            column names to select those columns
            
        rows : int | default ``20``
            How mant rows of the DataFrame to display.
            If rows < 0, displays the last 
            ``abs(rows)`` entries
            
        start: int | default ``0``
            What index to start displaying the DataFrame at
        
        title: str | default ``None``
            A title for the DataFrame to be displayed using
            ``show()``
        desc: bool | default ``True``
            Wether to display the DataFrame's size
        
        Returns
        –––––––
        None
        """
        if type(title) == str:
            show(title)
        elif title != None:
            show(title[0], title[1])
        settings = ['display.max_rows','display.max_columns',
                        'display.width','display.max_colwidth']
        [pd.set_option(i, None) for i in settings]
        loc, cols = 'head', self.columns
        if rows < 0:
            loc = 'tail'
        if columns != ["all"]:
            cols = columns
        if allrows:
            display(self[cols])
        if start or columns != ['all']:
            display(self[cols].iloc[start:start+rows , :])
        else:
            eval(f"display(self.{loc}({abs(rows)}))")
        [pd.reset_option(i) for i in settings]
        if desc:
            nrow, ncol = self.shape
            show(f"{nrow} Rows x {ncol} Columns", [])
pd.DataFrame.show = showtable


def visualize(data):
    @interact(Kind = widgets.Dropdown(options=["Scatter Plot", "Histogram"], value = None))
    def plot_kind(Kind):
        cols = widgets.Dropdown(options=data.columns)
        if Kind == "Scatter Plot":
            show(">***NOTE:*** If you chose `Color By` to be a column with numeric data, " \
                 + "that will **disable the `Side Graph`** parameter")
            @interact(x = widgets.Dropdown(options=data.columns, value = None, 
                                           description = "X-Axis"), 
                      y = widgets.Dropdown(options=data.columns, value = None, 
                                           description = "Y-Axis"),
                      color = widgets.Dropdown(options= [None] + list(data.columns), value = None, 
                                               description = "Color By"),
                     marginal = widgets.Dropdown(options = [None, 'rug', 'box', 'violin','histogram'], 
                                                 value = 'histogram', description = "Side Graph"))
            def scatter_helper(x, y, marginal, color):
                if color != None and data[color].dtype == float:
                    marginal = None
                if (x != None and y != None):
                    px.scatter(data_frame = data, 
                               x = x, y = y, 
                               color = color,
                               color_continuous_scale='viridis', 
                               template = 'seaborn',
                               marginal_x = marginal, marginal_y = marginal,
                               title = f"'{x}' vs. '{y}'").show()
        if Kind == "Histogram":
            show("Using the `Color By` variable here leads to some odd displays",
                 "They aren't really usefull, but we've the option to se it in case you are curious",
                 "The default `None` gives a solid color")
            @interact(x = widgets.Dropdown(options=data.columns, value = None,
                                          description = "X-Axis"),
                      color = widgets.Dropdown(options=[None] + list(data.columns), value = None,
                                              description = "Color By"),
                     marginal = widgets.Dropdown(options = [None, 'rug', 'box', 'violin','histogram'], 
                                                 value = 'box', description = "Top Graph"))
            def hist_helper(x, marginal, color):
                if (x != None):
                    px.histogram(data_frame = data, 
                               x = x,
                               color = color, template = "seaborn",
                                marginal = marginal,
                                title = f"Distribution of '{x}'").show()

def workshop_hist():
    @interact(data = Dropdown(options = [None] + list(tables.keys()), description = "Workshop"),
              showall = ToggleButton(value=False, description=f'Show All Plots', icon = "eye", 
                                     button_style = "warning"))
    def step_1(showall, data):
        if showall:
            @interact(mode = Dropdown(options = [("Stacked", 'relative'), ("Side-By-Side", 'group')]))
            def show_all(mode):
                errors = []
                for key in tables.keys():
                    df = tables[key]
                    for x in df.columns:
                        for color in df.columns:
                            if (x != color):
                                try:
                                    px.histogram(data_frame = df, 
                                           x = x,
                                               color = color, 
                                                     template = "seaborn",
                                                         title = f"Distribution of '{x}'",
                                                            barmode = mode).show()
                                except Exception as e:
                                    errors.append(f"Encountered {e} when attempting to plot {x} from {key}, colored by {color}")
                for error in errors:
                    show(error, tags=["pre style='font-size:15px'"])
                        
                    
        elif data:
            key = data
            data = tables[data]
            @interact(x = widgets.Dropdown(options=data.columns, value = None,
                                                  description = "X-Axis"),
                              color = widgets.Dropdown(options=[i for i in [None] + list(data.columns) 
                                                                if i != "Feedback"], value = None,
                                                       description = "Color By"),
                     mode = Dropdown(options = [("Stacked", 'relative'), ("Side-By-Side", 'group')]))
            def hist_helper(x, color, mode):
                if x == "Feedback":
                    feedback = data["Feedback"]
                    for comment in feedback:
                        if pd.notna(comment):
                                show("*" + comment, tags=["pre style='font-size: 18px'"])
                                show("\n")
                            
                            
                elif (x != None):
                    try:
                        px.histogram(data_frame = data, 
                                   x = x,
                                   color = color, template = "seaborn",
                                    title = f"Distribution of '{x}'",
                                    barmode = mode).show()
                    except Error as e:
                        f"Encountered {e} when attempting to plot {x} from {key}," \
                        + f"colored by {color}"