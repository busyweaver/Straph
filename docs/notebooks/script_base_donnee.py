#sigmasv_links.sg
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (15,10)
import straph as sg
import straph.betweenness as bt
import straph.betweenness.volumes as vol
import straph.paths.meta_walks as mw
import operator

file_name = "examples/primary_school/primaryschool.csv"
entry_format = {"u_pos": 1, "v_pos": 2, "t_pos": 0}
config = {"delimiter": "\t", "ignore_header": False, "nodes_to_label": True, "time_is_datetime": False,
          "is_link_stream" : True}
sg.sort_csv(file_name, entry_format, **config)
S = sg.parser(input_file=file_name,
           input_format='csv',
           entry_format=entry_format,
           output_file="high_school_2013",
           output_format='sg',
           **config)

b = operator.lt
walk_type = "passive"
fun =  mw.Metawalk.co_sfp

events, events_reverse = bt.events_dic(S)

exact_between, betweenness ,features = bt.betweenness_all_dis_gen(S, b, fun, walk_type, approx = 1)
