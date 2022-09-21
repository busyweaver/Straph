#sigmasv_links.sg
import pandas as pd
import straph as sg
import straph.betweenness as bt
import straph.paths.meta_walks as mw
import operator



networks = ["examples/primary_school/primaryschool.csv"]
for net in networks:
    file_name = net
    entry_format = {"u_pos": 1, "v_pos": 2, "t_pos": 0}
    config = {"delimiter": "\t", "ignore_header": False,
              "nodes_to_label": True, "time_is_datetime": False,"is_link_stream" : True}
    sg.sort_csv(file_name, entry_format, **config)
    S = sg.parser(input_file=file_name,
           input_format='csv',
           entry_format=entry_format,
           output_file="high_school_2013",
           output_format='sg',
           **config)
    bt.computation_betweenness_many_optimal_dis_gen(S, "primary", approx = -1)
